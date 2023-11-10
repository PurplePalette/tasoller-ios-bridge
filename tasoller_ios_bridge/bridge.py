import time
from dataclasses import dataclass

from tasoller_ios_bridge import frida, tasoller


class TouchType:
    UNDEFINED = -1
    RELEASE = 0
    PRESS = 1
    MOVE = 2


@dataclass
class TasollerTouch:
    identifier: int
    side_start: int
    side_end: int
    touch_type: int = TouchType.RELEASE


@dataclass
class SimulateTouch:
    tid: int
    x: int
    y: int
    ttype: int = TouchType.RELEASE


class Bridge:
    def __init__(
        self,
        frida_host: str = "localhost",
        frida_port: int = 27042,
        base_color: tasoller.Color = [0x10, 0x00, 0x10],
        bar_color: tasoller.Color = [0x20, 0x00, 0x20],
        touch_color: tasoller.Color = [0xFF, 0x00, 0x00],
        touch_screen_x_area: tuple[int, int] = None,
        touch_screen_y: int = None,
        reverse: bool = False,
    ) -> None:
        self.tasoller = tasoller.Tasoller(
            id_vendor=0x1CCF,
            id_product=0x2333,
            base_color=base_color,
            bar_color=bar_color,
            touch_color=touch_color,
        )
        self.frida = frida.Frida(frida_host, frida_port)

        self.available_identifiers: list[int] = list(range(10))
        self.previous_touches: list[TasollerTouch] = []
        self.current_touches: list[TasollerTouch] = []

        self.touch_screen_x_area: tuple[int, int] = touch_screen_x_area
        self.touch_screen_y: int = touch_screen_y
        self.reverse: bool = reverse

    def __map_float(self, value, start1, stop1, start2, stop2):
        return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

    def get_new_identifier(self):
        self.available_identifiers.sort()
        return self.available_identifiers.pop(0)

    def release_identifier(self, identifier):
        self.available_identifiers.insert(0, identifier)

    def get_current_touches_from_slider_state(self):
        touch_process: bool = False
        for i in range(0, 16):
            touch_state = self.tasoller.get_slider_state(i)
            if touch_state and not touch_process:
                touch_process = True
                self.current_touches.append(
                    TasollerTouch(-1, i, i, TouchType.UNDEFINED)
                )
            elif touch_state and touch_process:
                self.current_touches[-1].side_end = i
            elif not touch_state and touch_process:
                touch_process = False
            if i == 15 and touch_state:
                touch_process = False
                self.current_touches[-1].side_end = i

    def inherit_touch_identifers(self):
        for prev_touch in self.previous_touches:
            released = True
            for cur_touch in self.current_touches:
                if cur_touch.identifier != -1:
                    continue
                if (
                    prev_touch.side_start - 1
                    < cur_touch.side_start
                    < prev_touch.side_end + 1
                    or prev_touch.side_start - 1
                    < cur_touch.side_end
                    < prev_touch.side_end + 1
                ):
                    cur_touch.identifier = prev_touch.identifier
                    cur_touch.touch_type = TouchType.MOVE
                    released = False
                    break
            if released:
                prev_touch.touch_type = TouchType.RELEASE

    def assign_touch_identifiers(self):
        self.available_identifiers.sort()
        for cur_touch in self.current_touches:
            if cur_touch.identifier == -1:
                cur_touch.identifier = self.get_new_identifier()
                cur_touch.touch_type = TouchType.PRESS

    def update_current_touches(self):
        self.current_touches.clear()
        self.get_current_touches_from_slider_state()
        self.inherit_touch_identifers()
        self.assign_touch_identifiers()

    def get_simulate_touches_from_current_touches(self):
        touch_events: list[SimulateTouch] = []

        # Touch and Move
        for touch in self.current_touches:
            center = (touch.side_start + touch.side_end) / 2
            touch_x = self.__map_float(
                center, 0, 15, self.touch_screen_x_area[0], self.touch_screen_x_area[1]
            )
            touch_y = self.touch_screen_y
            if self.reverse:
                touch_x, touch_y = touch_y, touch_x
            if touch.touch_type == TouchType.PRESS:
                touch_events.append(
                    SimulateTouch(
                        touch.identifier, int(touch_x), int(touch_y), TouchType.PRESS
                    )
                )
            elif touch.touch_type == TouchType.MOVE:
                touch_events.append(
                    SimulateTouch(
                        touch.identifier, int(touch_x), int(touch_y), TouchType.MOVE
                    )
                )
        # Release
        for touch in self.previous_touches:
            if touch.touch_type == TouchType.RELEASE:
                center = (touch.side_start + touch.side_end) / 2
                touch_x = self.__map_float(
                    center,
                    0,
                    15,
                    self.touch_screen_x_area[0],
                    self.touch_screen_x_area[1],
                )
                touch_y = self.touch_screen_y
                touch_events.append(
                    SimulateTouch(
                        touch.identifier, int(touch_x), int(touch_y), TouchType.RELEASE
                    )
                )
                self.release_identifier(touch.identifier)
        return touch_events

    def send_simulate_touches_to_ios(self, touch_events: list[SimulateTouch]):
        for touch_event in touch_events:
            self.frida.script.post(
                {
                    "type": "in",
                    "tid": touch_event.tid,
                    "x": touch_event.x,
                    "y": touch_event.y,
                    "ttype": touch_event.ttype,
                }
            )

    def update(self):
        self.tasoller.update()
        self.update_current_touches()
        touch_events = self.get_simulate_touches_from_current_touches()
        self.send_simulate_touches_to_ios(touch_events)
        self.previous_touches = self.current_touches.copy()

    def run(self):
        while True:
            self.update()
            time.sleep(0.01)

from typing import NewType

import libusb_package
from usb.core import Device

Color = NewType("Color", list[int, int, int])


class Tasoller:
    THRESHOLD = 20
    AIR_1 = 1
    AIR_2 = 2
    AIR_3 = 4
    AIR_4 = 8
    AIR_5 = 16
    AIR_6 = 32
    FN_1 = 64
    FN_2 = 128

    def __init__(
        self,
        id_vendor: int = 0x1CCF,
        id_product: int = 0x2333,
        base_color: Color = [0x10, 0x00, 0x10],
        bar_color: Color = [0x20, 0x00, 0x20],
        touch_color: Color = [0xFF, 0x00, 0x00],
    ) -> None:
        self.base_color: Color = base_color
        self.bar_color: Color = bar_color
        self.touch_color: Color = touch_color

        self.tasoller: Device = libusb_package.find(
            idVendor=id_vendor, idProduct=id_product
        )

        if self.tasoller is None:
            raise ValueError("Tasoller not found")
        self.tasoller.set_configuration()
        self.state = self.update()

    def get_slider_state(self, lane):
        # lane is 0-15
        return (
            self.state[4 + lane * 2] >= Tasoller.THRESHOLD
            or self.state[4 + lane * 2 + 1] >= Tasoller.THRESHOLD
        )

    def get_color_msg(self, color_list: list[list[int, int, int]]) -> list[int]:
        # starting header (no idea what this does, but message will be ignored if first two bytes are wrong)
        msg = [0x42, 0x4C, 0x00]
        # msg = []

        # Color format appears to be Green, Red, Blue.
        for color in color_list:
            msg += color
        if len(color_list) < 31:
            msg += [0x00, 0x00, 0x00] * (31 - len(color_list))
        # msg += [g, r, b] * 31 # touch bar, right to left
        msg += [0x00, 0x00, 0xFF] * 24  # left sensor, top to bottom
        msg += [0x00, 0x00, 0xFF] * 24  # right sensor, bottom to top

        # pad message to 240 bytes
        msg += [0x00] * (240 - len(msg))
        return msg

    def swap_rgb(self, color):
        return [color[1], color[0], color[2]]

    def illuminate_led(self):
        color_list = []
        for i in range(0, 31):
            if i % 2 == 0:
                color_list.append(self.swap_rgb(self.base_color))
            else:
                color_list.append(self.swap_rgb(self.bar_color))
        for i in range(0, 16):
            if self.get_slider_state(i):
                color_list[31 - (2 * i + 1)] = self.swap_rgb(self.touch_color)
        self.tasoller.write(0x03, self.get_color_msg(color_list))

    def update(self):
        self.state = self.tasoller.read(0x84, 36, 100)
        self.illuminate_led()

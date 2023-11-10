import argparse

from tasoller_ios_bridge.bridge import Bridge

parser = argparse.ArgumentParser()
parser.add_argument(
    "--frida-host", type=str, default="localhost", help="Frida host(default: localhost)"
)
parser.add_argument(
    "--frida-port", type=int, default=27042, help="Frida port(default: 27042)"
)
parser.add_argument(
    "--base-color",
    type=str,
    default="16:00:16",
    help="TASOLLER LED color(r:g:b) when untouched(default: 16:00:16). Max: 255:255:255",
)
parser.add_argument(
    "--bar-color",
    type=str,
    default="32:00:32",
    help="TASOLLER LED bar color(r:g:b) (default: 32:00:32). Max: 255:255:255",
)
parser.add_argument(
    "--touch-color",
    type=str,
    default="255:00:00",
    help="TASOLLER LED color(r:g:b) when touched(default: 255:00:00). Max: 255:255:255",
)
parser.add_argument(
    "--touch-screen-x-area",
    type=str,
    default="200:1720",
    help="Width of X coordinate of screen to touch(default: 200:1720)",
)
parser.add_argument(
    "--touch-screen-y",
    type=int,
    default=800,
    help="Y coordinate of screen to touch(default: 800)",
)
parser.add_argument(
    "--reverse",
    action="store_true",
    default=False,
    help="Reverse of touch screen(default: False)",
)

args = parser.parse_args()

base_color = [int(x) for x in args.base_color.split(":")]
bar_color = [int(x) for x in args.bar_color.split(":")]
touch_color = [int(x) for x in args.touch_color.split(":")]
touch_screen_x_area = [int(x) for x in args.touch_screen_x_area.split(":")]
touch_screen_y = args.touch_screen_y
reverse = args.reverse

bridge = Bridge(
    frida_host=args.frida_host,
    frida_port=args.frida_port,
    base_color=base_color,
    bar_color=bar_color,
    touch_color=touch_color,
    touch_screen_x_area=touch_screen_x_area,
    touch_screen_y=touch_screen_y,
    reverse=reverse,
)
bridge.run()

import frida


class Frida:
    def __init__(self, host: str = "localhost", port: int = 27042) -> None:
        self.host = host
        self.port = port
        self.device = frida.get_device_manager().add_remote_device(
            f"{self.host}:{self.port}"
        )
        self.session = self.device.attach("Gadget")
        with open("scripts/_index.js", "r", encoding="utf-8") as f:
            js = f.read()
        self.script = self.session.create_script(js)
        self.script.load()

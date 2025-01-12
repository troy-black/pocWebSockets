from tdb.poc_websockets.server.config import ApplicationConfig


class ClientConfig(ApplicationConfig):
    USER: str
    PASS: str
    ROOM: str

    def __init__(self) -> None:
        super().__init__(setup_logging=False)


# Requires all Setting variables to exist in env
settings = ClientConfig()

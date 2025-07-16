class Scale:
    """Simulação da balança eletrônica"""

    def __init__(self, port: str = "COM1", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.is_connected = True  # Simulação

    def get_weight(self) -> float:
        return 0.0

    def tare(self) -> bool:
        return True

    def is_stable(self) -> bool:
        return True

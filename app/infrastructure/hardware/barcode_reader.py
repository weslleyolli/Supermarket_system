class BarcodeReader:
    """Simulação do leitor de código de barras"""

    def __init__(self, port: str = "auto"):
        self.port = port
        self.is_connected = True  # Simulação

    def read_barcode(self) -> str | None:
        return None

    def is_ready(self) -> bool:
        return self.is_connected

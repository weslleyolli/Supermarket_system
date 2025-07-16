class ThermalPrinter:
    """Simulação da impressora térmica"""

    def __init__(self, port: str = "COM2"):
        self.port = port
        self.is_connected = True  # Simulação

    def print_receipt(self, receipt_data: dict) -> bool:
        print("=== CUPOM FISCAL ===")
        print(f"Venda: {receipt_data.get('sale_id')}")
        print(f"Data: {receipt_data.get('date')}")
        print("-" * 30)
        for item in receipt_data.get("items", []):
            print(f"{item['name']}")
            if item.get("weight"):
                print(f"  {item['weight']:.3f}kg x R$ {item['unit_price']:.2f}")
            else:
                print(f"  {item['quantity']:.0f}un x R$ {item['unit_price']:.2f}")
            if item.get("discount", 0) > 0:
                print(f"  Desconto: -R$ {item['discount']:.2f}")
            print(f"  Total: R$ {item['total']:.2f}")
            print()
        print("-" * 30)
        print(f"Subtotal: R$ {receipt_data.get('subtotal', 0):.2f}")
        if receipt_data.get("total_discount", 0) > 0:
            print(f"Desconto: -R$ {receipt_data.get('total_discount', 0):.2f}")
        print(f"TOTAL: R$ {receipt_data.get('final_total', 0):.2f}")
        print(f"Pagamento: {receipt_data.get('payment_method', '').upper()}")
        print(f"Recebido: R$ {receipt_data.get('amount_received', 0):.2f}")
        print(f"Troco: R$ {receipt_data.get('change', 0):.2f}")
        print("=" * 30)
        return True

    def open_drawer(self) -> bool:
        print("🔓 Gaveta do dinheiro aberta")
        return True

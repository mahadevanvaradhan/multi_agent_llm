from pydantic import BaseModel

class Order(BaseModel):
    order_id: str
    userid: int
    product: str
    cost: float
    quantity: int
    order_date: str
    shipment_id: str
    order_status: str

def load_orders_from_json(file_path: str) -> list[Order]:
    """
    Loads order data from a JSON file.

    Args:
        file_path: The path to the JSON file containing order data.

    Returns:
        A list of Order objects parsed from the JSON file.
    """
    import json
    with open(file_path, "r") as f:
        data = json.load(f)
    return [Order(**order) for order in data]
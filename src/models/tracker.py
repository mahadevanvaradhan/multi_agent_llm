from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

class Shipment(BaseModel):
    shipment_id: str
    pin_code: str
    shipment_status: str
    last_update: str
    comments: str


def load_shipments_from_json(file_path: str) -> list[Shipment]:
    """
    Loads shipment data from a JSON file.

    Args:
        file_path: The path to the JSON file containing shipment data.

    Returns:
        A list of Shipment objects parsed from the JSON file.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return [Shipment(**shipment) for shipment in data]

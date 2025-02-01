from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

class Product(BaseModel):
    """
    Represents a product with its details.
    """
    product_name: str
    description: str
    usage: str
    summary: str
    cost: float 

def load_products_from_json(file_path: str) -> list[Product]:
    """
    Loads shipment data from a JSON file.

    Args:
        file_path: The path to the JSON file containing shipment data.

    Returns:
        A list of Shipment objects parsed from the JSON file.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return [Product(**product) for product in data]

from pydantic import BaseModel

# Define the Product model
class Product(BaseModel):
    """
    Represents a product with its details.
    """
    product_name: str
    description: str
    usage: str
    summary: str
    cost: float
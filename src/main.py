# app.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re
from openai import OpenAI
import anthropic
import voyageai
import os
from fastapi.responses import JSONResponse
import uuid
import requests
import json

from src.models.products import Product
from src.models.orders import Order, load_orders_from_json
from src.models.tracker import Shipment, load_shipments_from_json
from src.models.anthropic_llm import anthropic_llm
from src.utils.voyage_operators import voyageai_embed_document
from src.utils.postgres_operators import query_pgvector

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')

openai_client = OpenAI(api_key=OPEN_API_KEY)
vo_client = voyageai.Client(api_key=VOYAGE_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

app = FastAPI()

# Load order data from JSON file
order_data = load_orders_from_json("/usr/local/chatbot/src/data/order.json")  # Replace with your path

# Load shipment data from JSON file
shipment_data = load_shipments_from_json("/usr/local/chatbot/src/data/tracker.json") 

# Load product data from JSON file
# product_data = load_products_from_json("/usr/local/chatbot/src/data/product.json") 

@app.get("/hello")
def index():
    return "WELCOME TO FAST API"

# @app.get("/products")
# async def get_all_products():
#     """
#     Fetches all products information.

#     Args:
#         No args.

#     Returns:
#         The product details as a JSON object.
#     """
#     product_data = load_products_from_json("/usr/local/chatbot/src/data/product.json") 

#     return product_data

@app.get("/orders/{order_id}")
async def get_orders(order_id: str):
    """
    Fetches order details by order ID.

    Args:
        order_id: The unique identifier of the order.

    Returns:
        The order details as a JSON object.
    """
    for order in order_data:
        if order.order_id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.get("/shipments/{shipment_id}")
async def get_shipment_history(shipment_id: str):
    """
    Fetches complete shipment history by shipment ID.

    Args:
        shipment_id: The unique identifier of the shipment.

    Returns:
        A list of ShipmentHistory objects representing the entire history.
    """
    history = [shipment for shipment in shipment_data if shipment.shipment_id == shipment_id]
    if not history:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return history

@app.get("/shipment_details/{order_id}")
async def get_order_with_shipment_history(order_id: str):
    """
    Fetches order details with shipment history by order ID.

    Args:
        order_id: The unique identifier of the order.

    Returns:
        A dictionary containing order details and shipment history.
    """
    try:
        order = next(order for order in order_data if order.order_id == order_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail="Order not found")

    shipment_history = [shipment for shipment in shipment_data if shipment.shipment_id == order.shipment_id]

    return {
        "order": order.dict(),
        "shipment_details": shipment_history
    }

# Function to call the external API
def get_order_details_from_api(order_id: str):
    """
    Fetches order details from the external API.

    Args:
        order_id: The unique identifier of the order.

    Returns:
        A dictionary containing order details and shipment history.
    """
    try:
        response = requests.get(f"http://localhost:8000/shipment_details/{order_id}")
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching order details: {e}")
        return {"error": f"Failed to fetch order details for order ID {order_id}"}
    
@app.post("/anthropic_ai_chat")
async def anthropic_ai_chat(user_query: str):
    """
    Handles user queries and provides responses using the LLM.

    Args:
        user_input: The user's message.

    Returns:
        A dictionary containing the response.
    """
    response = anthropic_llm(anthropic_client, user_query, model="claude-3-sonnet-20240229")
    return response


async def process_tool_call(tool_name, tool_input):
    if tool_name == "get_orders":
        return get_orders(tool_input["order_id"])
    elif tool_name == "get_shipment_history":
        return get_shipment_history(tool_input["shipment_id"])
    elif tool_name == "get_order_with_shipment_history":
        return get_order_with_shipment_history(tool_input["order_id"])
    else:
        raise ValueError(f"Unknown tool: {tool_name}")



@app.post("/anthropic_agent_multifunction")
async def anthropic_agent_multifunction(user_query):

    query_embedding = voyageai_embed_document(user_query)

    content = query_pgvector(query_embedding)
    # Convert the results to Document objects for LlamaIndex
    knowledge_base = [item[0] for item in content]

    tools = [
                {
                "name": "get_orders",
                "description": "This function is used to provide details of a specific order by its unique Order ID. \
                                It includes details like User ID, Product Name, Cost, Quantity of order, Order Date, Shipment ID and current Status Of Order.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The Order ID of the order."
                        }
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "get_shipment_history",
                "description": "This function is used to provide complete details of shipment history for a Shipment ID. \
                    It helps to track an order from the date it is ordered and different stages of shippment involved ducring package shipments. \
                    It also provides each stages of shipment like packed, dispatched, out for delivery, delivered, and returned along with date.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "shipment_id": {
                            "type": "string",
                            "description": "The Shipment ID of the shipment."
                        }
                    },
                    "required": ["shipment_id"]
                }
            },
            {
                "name": "get_order_with_shipment_history",
                "description": "This function is used to provide complete details of Order and shipment history for a Provide Order ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The Order ID of the order."
                        }
                    },
                    "required": ["order_id"]
                }
            }
        ]

    prompt = f"""
    You are a support assistant. 
    Your job is to answer user queries based on the following knowledge base and use available tools when required.
    Whenever customers enquires about their order status, ask for Order ID or Shipment ID if it is not available in the conversation.

    Star with the summary of their order in few lines, and provide details of the ir order in new section.

    Knowledge Base:
    {knowledge_base}

    Tools:
    {json.dumps(tools, indent=2)}

    User Query:
    {user_query}

    If the answer is directly available in the knowledge base, respond with it. 
    If you need to use a tool, specify the tool and its parameters.
    Provide answers in readbale and formatted text.
    """
    history = []

    messages = [
        {"role": "user", "content": prompt}
    ]

    # Mocked `anthropic_client` for demonstration purposes
    response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )

    # print(f"\nInitial Response:")
    # print(f"Stop Reason: {response.stop_reason}")
    # print(f"Content: {response.content}")

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input

        # print(f"\nTool Used: {tool_name}")
        # print(f"Tool Input:")
        # print(json.dumps(tool_input, indent=2))

        tool_result = await process_tool_call(tool_name, tool_input)

        # print(f"\nTool Result:")
        # print(json.dumps(tool_result, indent=2))

        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(tool_result),
                    }
                ],
            },
        ]

        # Mocked `anthropic_client` for demonstration purposes
        response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        tools=tools,
        messages=messages
        )

        # print(f"\nResponse:")
        # print(f"Stop Reason: {response.stop_reason}")
        # print(f"Content: {response.content}")

    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )

    # print(f"\nFinal Response: {final_response}")

    # history.append((user_query, final_response))

    return final_response
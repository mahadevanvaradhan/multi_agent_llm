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
import gradio as gr

from src.models.products import Product
from src.models.orders import Order, load_orders_from_json
from src.models.tracker import Shipment, load_shipments_from_json
from src.models.anthropic_llm import anthropic_llm
from src.utils.voyage_operators import voyageai_embed_document
from src.utils.postgres_operators import query_pgvector
from src.main import anthropic_agent_multifunction 

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')

openai_client = OpenAI(api_key=OPEN_API_KEY)
vo_client = voyageai.Client(api_key=VOYAGE_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# Gradio async wrapper
async def gradio_chatbot(user_query, history):
    response = await anthropic_agent_multifunction(user_query)
    history = history or []
    history.append((user_query, response))
    return history, history

if __name__ == "__main__":
    # Gradio interface setup
    with gr.Blocks() as demo:
        chatbot_ui = gr.Chatbot(label="AI Chatbot with Tools")
        message = gr.Textbox(label="Your Query", placeholder="Ask me anything...", lines=1)
        state = gr.State()  # For chat history
        send_button = gr.Button("Send")

        send_button.click(
            fn=gradio_chatbot,
            inputs=[message, state],
            outputs=[chatbot_ui, state],
            api_name="chat"
        )
    demo.launch(server_port=7861, share=True)
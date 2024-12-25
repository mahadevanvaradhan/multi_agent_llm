
import os
import json
import pandas as pd
import nltk
import anthropic

tools = [
            {
                "name": "get_order",
                "description": "Fetches details of a specific order by its unique identifier.",
                "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                    "type": "string",
                    "description": "The unique identifier of the order."
                    }
                },
                "required": ["order_id"]
                }
            },
            {
                "name": "get_shipment_history",
                "description": "Fetches the complete shipment history of a specific shipment by its unique identifier.",
                "parameters": {
                "type": "object",
                "properties": {
                    "shipment_id": {
                    "type": "string",
                    "description": "The unique identifier of the shipment."
                    }
                },
                "required": ["shipment_id"]
                }
            },
            {
                "name": "get_order_with_shipment_history",
                "description": "Fetches details of a specific order and its related shipment history by the order's unique identifier.",
                "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                    "type": "string",
                    "description": "The unique identifier of the order."
                    }
                },
                "required": ["order_id"]
                }
            }
        ]


def anthropic_llm(anthropic_client, user_query, content):

    # Format the prompt with cullet data and user query
    prompt = f"""You are a support chatbot, serving as a customer support assistant. 
            Your primary role is to answer customer questions: {user_query} and 
            provide detailed, accurate responses strictly based on the knowledge base: {content}. 
            The knowledge base has section like product name, summary, description, usage and cost.
            Always provide output in readable markdown language. 
            """
    print(prompt)
    response = anthropic_client.messages.create(
                model = "claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,
            )
    print(response)
    # Retrieve and return the model's response
    answer = response.content[0].text
    return answer



import os
import json
import pandas as pd
import nltk
import anthropic
from src.utils.voyage_operators import voyageai_embed_document
from src.utils.postgres_operators import query_pgvector



def anthropic_llm(anthropic_client, user_query, model = "claude-3-sonnet-20240229"):

    query_embedding = voyageai_embed_document(user_query)

    content = query_pgvector(query_embedding)
    # Convert the results to Document objects for LlamaIndex
    documents = [item[0] for item in content]

    # Format the prompt with cullet data and user query
    prompt = f"""You are a support chatbot, serving as a customer support assistant. 
            Your primary role is to answer customer questions: {user_query} and 
            provide detailed, accurate responses strictly based on the knowledge base: {documents}. 
            The knowledge base has section like product name, summary, description, usage and cost.
            Always provide output in human readable format, apply headings, section and list wherever applicable. 
            """
    print(prompt)
    response = anthropic_client.messages.create(
                model = model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,
            )
    print(response)
    # Retrieve and return the model's response
    answer = response.content[0].text
    return answer

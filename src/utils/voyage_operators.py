import os
import anthropic
import voyageai

VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')
vo_client = voyageai.Client(api_key=VOYAGE_API_KEY)

def voyageai_embed_document(document, model="voyage-3-large", input_type="document", output_dimension=1024):
    """
    Embeds a document using Voyage embeddings.

    Parameters:
    - document: The text document to embed.
    - model: The embedding model to use.
    - input_type: The type of input (e.g., "document").
    - output_dimension: 1024

    Returns:
    - Embedding as a list of floats.
    """
    try:
        embedding = vo_client.embed([document], model=model, input_type=input_type, output_dimension=output_dimension).embeddings[0]
        return embedding
    except Exception as e:
        print(f"Error embedding document: {e}")
        return None
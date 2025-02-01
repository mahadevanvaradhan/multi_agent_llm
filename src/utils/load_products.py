import json
from pydantic import BaseModel
from typing import List
import os
import anthropic
import voyageai
import psycopg2
from src.models.products import Product
from src.database import get_db_connection
from src.utils.voyage_operators import voyageai_embed_document

VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
vo_client = voyageai.Client(api_key=VOYAGE_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def load_products_from_json(file_path: str) -> List[Product]:
    """
    Loads product data from a JSON file.

    Args:
        file_path: The path to the JSON file containing product data.

    Returns:
        A list of Product objects parsed from the JSON file.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return [Product(**product) for product in data]

def generate_document(product: Product) -> str:
    """
    Creates a Markdown-formatted document from product details.
    """
    return f"""# {product.product_name}
                **Description:**  
                {product.description}

                **Usage:**  
                {product.usage}

                **Summary:**  
                {product.summary}

                **Cost:**  
                ${product.cost:.2f}
                """


## Function to create vector extension in Postgres database
def manage_vector_extension():


    conn = get_db_connection()
    if not conn:
        return 
    try:
        # Establishing the connection
        # Connect to PostgreSQL
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
        exists = cursor.fetchone()

        if not exists:
            print("ℹ️ 'vector' extension not found. Creating it...")
            cursor.execute("CREATE EXTENSION vector;")
            print("✅ 'vector' extension created successfully.")
        else:
            print("✅ 'vector' extension already exists.")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Ensure cursor and connection are closed properly
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def insert_products_to_postgres(products: List[Product]):
    """
    Inserts product data into a PostgreSQL database with embeddings.

    Args:
        products: A list of Product objects.
        db_config: Dictionary containing PostgreSQL connection details.
    """

    conn = get_db_connection()
    if not conn:
        return 
    try:
        # Connect to PostgreSQL
        cursor = conn.cursor()
        manage_vector_extension()
        # Create table if not exists
        cursor.execute("""
            DROP TABLE IF EXISTS products;
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                document TEXT NOT NULL,
                embedding VECTOR(1024)  -- Adjust dimension as per Voyage AI model
            )
        """)
        conn.commit()

        # Insert data with embeddings
        for product in products:
            document = generate_document(product)
            embedding = voyageai_embed_document(document)

            if embedding:  # Ensure embedding is generated
                cursor.execute("""
                    INSERT INTO products (document, embedding)
                    VALUES (%s, %s)
                """, (document, embedding))
        
        conn.commit()
        print(f"✅ {len(products)} products inserted successfully into PostgreSQL.")

    except Exception as e:
        print(f"❌ Error inserting data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Load products from JSON
    json_file_path = "/usr/local/chatbot/src/data/product.json"  
    # Replace with actual path
    products = load_products_from_json(json_file_path)
    # Insert into PostgreSQL
    insert_products_to_postgres(products)

from pydantic import BaseModel
from typing import List
import os
import psycopg2
from src.database import get_db_connection

def query_pgvector(query_embedding, table_name='products', output_column='document', embedding_column='embedding', top_n=10):
    """
    Queries a PostgreSQL pgvector table to find the most similar documents.
    
    Args:
        query_embedding (list[float]): The embedding vector to search for.
        table_name (str): The name of the table to query.
        output_column (str): The column to return as output.
        embedding_column (str): The vector column used for similarity search.
        top_n (int): Number of top results to return.

    Returns:
        list: List of tuples with matching results.
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()

        # Convert embedding to PostgreSQL ARRAY format
        embedding_str = f"ARRAY{query_embedding}"  # Example: ARRAY[0.12, 0.34, 0.56, ...]

        # Use parameterized query to avoid SQL injection
        query = f"""SELECT 
                pge.{output_column},
                (1 - (pge.{embedding_column} <=> {embedding_str}::vector)) AS cosine_similarity
                    FROM 
                        public.{table_name} AS pge
                    ORDER BY cosine_similarity DESC
                    LIMIT {top_n};
                """
        
        # Execute query safely using parameters
        cursor.execute(query)
        results = cursor.fetchall()

        return results

    except Exception as e:
        print("❌ Error:", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

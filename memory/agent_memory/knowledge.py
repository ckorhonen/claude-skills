"""Agno Knowledge integration for storing and retrieving agent learnings."""

from typing import Any
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agent_memory.config import DB_URL, EMBEDDING_MODEL


def _get_vector_db() -> PgVector:
    """Initialize and return the PgVector database instance."""
    return PgVector(
        table_name="agent_learnings",
        db_url=DB_URL,
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id=EMBEDDING_MODEL),
    )


def search_learnings(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Search for relevant learnings based on a query.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A list of learning dictionaries. Returns empty list on error.
    """
    try:
        vector_db = _get_vector_db()
        results = vector_db.search(query=query, limit=max_results)

        if not results:
            return []

        # Extract the payload from each result
        learnings = []
        for result in results:
            if hasattr(result, 'payload') and result.payload:
                learnings.append(result.payload)
            elif isinstance(result, dict) and 'payload' in result:
                learnings.append(result['payload'])

        return learnings
    except Exception as e:
        print(f"Error searching learnings: {e}")
        return []


def save_learning(payload: dict[str, Any]) -> None:
    """
    Save a learning to the vector database.

    Args:
        payload: Dictionary containing the learning data with schema:
            - title (str): Title of the learning
            - context (str): Context in which this applies
            - learning (str): The actual learning/insight
            - confidence (str): One of 'low', 'medium', 'high'
            - type (str): One of 'rule', 'heuristic', 'source', 'process', 'constraint'
            - created_at (str): RFC3339 timestamp
            - repo (str): Repository identifier
            - tags (list[str], optional): Optional tags for categorization

    Raises:
        Exception: If saving fails
    """
    try:
        vector_db = _get_vector_db()

        # Create a searchable text from the payload
        search_text = f"{payload.get('title', '')} {payload.get('learning', '')} {payload.get('context', '')}"

        # Insert the learning
        vector_db.insert(
            documents=[search_text],
            payloads=[payload],
        )
    except Exception as e:
        raise Exception(f"Error saving learning: {e}") from e

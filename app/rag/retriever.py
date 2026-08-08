from app.rag.vector_store import VectorStore


class Retriever:
    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()

    def retrieve_chunks(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieves top matching knowledge chunks for a query."""
        return self.vector_store.search(query, top_k=top_k)

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves and formats matching knowledge chunks as markdown text for LLM injection."""
        chunks = self.retrieve_chunks(query, top_k=top_k)
        if not chunks:
            return ""

        formatted_snippets = []
        for idx, chunk in enumerate(chunks, 1):
            title = chunk.get("title", "Reference Snippet")
            content = chunk.get("content", "").strip()
            formatted_snippets.append(f"--- Context Snippet {idx}: {title} ---\n{content}")

        return "\n\n".join(formatted_snippets)

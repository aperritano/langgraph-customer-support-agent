"""Vector store for knowledge base using InMemoryVectorStore."""

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import json
from pathlib import Path
from typing import Optional


class KnowledgeBaseVectorStore:
    """Manages the knowledge base vector store."""

    def __init__(self, embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the vector store with embeddings model.

        Args:
            embeddings_model: HuggingFace model name for embeddings
        """
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store: Optional[InMemoryVectorStore] = None

    def load_from_json(self, json_path: str) -> None:
        """Load knowledge base from JSON file and populate vector store.

        Args:
            json_path: Path to knowledge_base.json file
        """
        # Read JSON file
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Convert JSON to documents
        documents = self._json_to_documents(data)

        # Create vector store
        self.vector_store = InMemoryVectorStore.from_documents(
            documents=documents,
            embedding=self.embeddings
        )

        print(f"✅ Loaded {len(documents)} documents into vector store")

    def _json_to_documents(self, data: dict) -> list[Document]:
        """Convert JSON knowledge base to LangChain documents.

        Args:
            data: Knowledge base dictionary

        Returns:
            List of Document objects
        """
        documents = []
        kb = data.get("knowledge_base", {})

        # Process policies
        policies = kb.get("policies", {})

        # Returns policy
        if "returns" in policies:
            returns = policies["returns"]
            content = f"""Return Policy:
- Time limit: {returns.get('time_limit', 'N/A')}
- Condition: {returns.get('condition', 'N/A')}
- Refund processing time: {returns.get('refund_time', 'N/A')}
- Return shipping cost: Free for defective items, ${returns.get('return_shipping', {}).get('other', 'N/A')} for other reasons
"""
            documents.append(Document(
                page_content=content,
                metadata={"category": "return", "type": "policy"}
            ))

        # Shipping policy
        if "shipping" in policies:
            shipping = policies["shipping"]
            content = "Shipping Options:\n"
            for method, details in shipping.items():
                content += f"- {method.title()}: {details.get('time', 'N/A')} - {details.get('cost', 'N/A')}\n"
            documents.append(Document(
                page_content=content,
                metadata={"category": "shipping", "type": "policy"}
            ))

        # Warranty policy
        if "warranty" in policies:
            warranty = policies["warranty"]
            content = f"""Warranty Information:
- Standard warranty: {warranty.get('standard', 'N/A')}
- Coverage: {warranty.get('coverage', 'N/A')}
- Extended warranty available: {'Yes' if warranty.get('extended_available') else 'No'}
"""
            documents.append(Document(
                page_content=content,
                metadata={"category": "product", "type": "policy"}
            ))

        # Payment policy
        if "payment" in policies:
            payment = policies["payment"]
            methods = ", ".join(payment.get('methods', []))
            content = f"""Payment Information:
- Accepted methods: {methods}
- Payment processor: {payment.get('processor', 'N/A')}
- Security: {payment.get('security', 'N/A')}
- Payment timing: Charged when order ships
"""
            documents.append(Document(
                page_content=content,
                metadata={"category": "payment", "type": "policy"}
            ))

        # Products
        products = kb.get("products", {})
        if "categories" in products:
            categories = ", ".join(products["categories"])
            content = f"Product Categories: {categories}"
            documents.append(Document(
                page_content=content,
                metadata={"category": "product", "type": "info"}
            ))

        if "top_products" in products:
            for product in products["top_products"]:
                features = ", ".join(product.get("features", []))
                content = f"""{product.get('name', 'Unknown Product')}
Price: {product.get('price', 'N/A')}
Features: {features}
"""
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "category": "product",
                        "type": "product_info",
                        "product_name": product.get("name", "")
                    }
                ))

        # FAQs
        for faq in kb.get("faq", []):
            content = f"""Question: {faq.get('question', '')}
Answer: {faq.get('answer', '')}
"""
            documents.append(Document(
                page_content=content,
                metadata={"category": "general", "type": "faq"}
            ))

        # Add general support info
        documents.append(Document(
            page_content="""Customer Support Information:
- Hours: Monday-Friday, 9 AM - 6 PM EST
- Contact methods: Chat, email (support@store.com), phone (1-800-SUPPORT)
- Order modifications: Available within 1 hour of placing order
- Price matching: Available on identical items from authorized retailers
- Gift wrapping: Available for $5 per item with custom messages
""",
            metadata={"category": "general", "type": "info"}
        ))

        return documents

    def search(self, query: str, k: int = 3, filter_category: Optional[str] = None) -> str:
        """Search the knowledge base for relevant information.

        Args:
            query: Search query
            k: Number of results to return
            filter_category: Optional category filter (return, shipping, payment, product, general)

        Returns:
            Formatted search results
        """
        if self.vector_store is None:
            return "Error: Vector store not initialized. Please load knowledge base first."

        # Perform similarity search
        if filter_category:
            # Create filter function that checks Document metadata
            def metadata_filter(doc: Document) -> bool:
                return doc.metadata.get("category") == filter_category

            results = self.vector_store.similarity_search(
                query,
                k=k,
                filter=metadata_filter
            )
        else:
            results = self.vector_store.similarity_search(query, k=k)

        if not results:
            return "No relevant information found in the knowledge base."

        # Format results
        formatted_results = []
        for i, doc in enumerate(results, 1):
            formatted_results.append(f"{doc.page_content.strip()}")

        return "\n\n".join(formatted_results)

    def search_with_scores(
        self,
        query: str,
        k: int = 5,
        filter_categories: Optional[list[str]] = None,
        score_threshold: float = 0.0
    ) -> list[tuple[Document, float]]:
        """Search the knowledge base with similarity scores.

        Args:
            query: Search query
            k: Number of results to return
            filter_categories: Optional list of categories to filter by
            score_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of (Document, score) tuples sorted by relevance
        """
        if self.vector_store is None:
            return []

        # Perform similarity search with scores
        if filter_categories:
            # Create filter function for multiple categories
            def metadata_filter(doc: Document) -> bool:
                return doc.metadata.get("category") in filter_categories

            results = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=metadata_filter
            )
        else:
            results = self.vector_store.similarity_search_with_score(query, k=k)

        # Filter by score threshold and return
        # Note: Lower scores mean higher similarity in some implementations
        # InMemoryVectorStore returns distance, so lower is better
        # We convert to similarity score (higher is better) for consistency
        filtered_results = []
        for doc, distance in results:
            # Convert distance to similarity (assuming cosine distance)
            # For normalized embeddings with cosine similarity:
            # similarity = 1 - distance
            similarity = 1.0 - distance

            if similarity >= score_threshold:
                filtered_results.append((doc, similarity))

        return filtered_results


# Global instance - initialized lazily
_vector_store_instance: Optional[KnowledgeBaseVectorStore] = None


def get_vector_store() -> KnowledgeBaseVectorStore:
    """Get or create the global vector store instance."""
    global _vector_store_instance

    if _vector_store_instance is None:
        _vector_store_instance = KnowledgeBaseVectorStore()

        # Load knowledge base from default location
        kb_path = Path(__file__).parent.parent.parent / "data" / "knowledge_base.json"
        if kb_path.exists():
            _vector_store_instance.load_from_json(str(kb_path))
        else:
            print(f"⚠️ Warning: Knowledge base not found at {kb_path}")

    return _vector_store_instance

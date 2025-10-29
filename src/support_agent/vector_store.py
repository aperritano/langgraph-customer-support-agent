"""Vector store for knowledge base using InMemoryVectorStore.

WHAT THIS FILE DOES:
Manages the semantic search functionality for the knowledge base. Converts text documents
into vector embeddings and enables similarity search - meaning you can search by meaning,
not just exact keyword matches.

WHY IT'S IMPORTANT:
Regular keyword search has limitations - it won't find "return policy" if you search for
"refund process". Vector/semantic search understands meaning, so it can find related
content even when the words don't match exactly. This makes the agent much better at
finding relevant information to answer customer questions.
"""

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import json
from pathlib import Path
from typing import Optional


class KnowledgeBaseVectorStore:
    """
    Manages the knowledge base vector store.
    
    WHAT IT IS:
    A class that handles converting knowledge base documents into searchable vectors
    and provides semantic search functionality. Think of it like Google's search
    engine but for your company's knowledge base - it finds relevant content based
    on meaning, not just keyword matching.
    
    WHY IT EXISTS:
    Without vector search, you'd need exact keyword matches. With vector search,
    the agent can find relevant information even when customer questions use different
    wording than what's in the knowledge base.
    """

    def __init__(self, embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the vector store with embeddings model.
        
        WHAT IT DOES:
        Sets up the embeddings model that converts text into vectors (numerical
        representations). These vectors capture the semantic meaning of text.

        WHY IT'S IMPORTANT:
        The embeddings model is what enables semantic search. Different models have
        different strengths - this one (all-MiniLM-L6-v2) is a good balance of
        speed and accuracy.

        Args:
            embeddings_model: HuggingFace model name for embeddings
                            (default is a fast, accurate model good for general use)
        """
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store: Optional[InMemoryVectorStore] = None

    def load_from_json(self, json_path: str) -> None:
        """
        Load knowledge base from JSON file and populate vector store.
        
        WHAT IT DOES:
        Reads the knowledge_base.json file, converts all the content (policies, FAQs,
        product info) into Document objects, then converts those into vector embeddings
        and stores them in the vector store.

        WHY IT'S IMPORTANT:
        This is the setup step that makes the knowledge base searchable. Without this,
        the search tools wouldn't have anything to search. This converts all your
        company knowledge into a format that can be semantically searched.

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
        """
        Convert JSON knowledge base to LangChain documents.
        
        WHAT IT DOES:
        Takes the raw JSON data and converts each piece of information (policies,
        FAQs, product info) into LangChain Document objects. Each document includes
        the content (text) and metadata (category, type) for filtering.

        WHY IT'S IMPORTANT:
        LangChain's vector store works with Document objects, not raw JSON. This method
        structures the knowledge base into a format that can be vectorized and searched.
        The metadata (category, type) allows filtering searches to specific areas.

        Args:
            data: Knowledge base dictionary from JSON file

        Returns:
            List of Document objects ready for vectorization
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
        """
        Search the knowledge base for relevant information.
        
        WHAT IT DOES:
        Performs semantic similarity search - converts the query to a vector, compares it
        against all documents in the vector store, and returns the most similar ones.
        Can optionally filter by category (e.g., only search return policies).

        WHY IT'S IMPORTANT:
        This is the core search functionality that tools use. When a customer asks "What's
        your return policy?", this finds the relevant return policy information even if
        the question uses different wording than what's in the knowledge base.

        HOW IT WORKS:
        1. Convert query to embedding (vector)
        2. Compare against all document embeddings using cosine similarity
        3. Return top k most similar documents
        4. Optional: Filter to specific category before searching

        Args:
            query: Customer's question or search terms
            k: Number of results to return (default: 3)
            filter_category: Optional category filter (return, shipping, payment, product, general)
                            Only searches documents in that category

        Returns:
            Formatted search results as a string
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
        """
        Search the knowledge base with similarity scores.
        
        WHAT IT DOES:
        Same as search() but also returns similarity scores for each result. Scores indicate
        how relevant each result is (0.0 = not relevant, 1.0 = very relevant). This allows
        filtering out low-relevance results and showing customers how confident the match is.

        WHY IT'S IMPORTANT:
        Sometimes search results aren't very relevant. With scores, you can:
        - Filter out results below a certain relevance threshold
        - Show users how confident the match is
        - Debug why certain searches aren't working (low scores indicate poor matches)
        - Make the agent smarter by only using highly-relevant information

        Args:
            query: Customer's question or search terms
            k: Maximum number of results to return
            filter_categories: Optional list of categories to filter by (can search multiple)
            score_threshold: Minimum similarity score (0.0 to 1.0) - filters out low-relevance results

        Returns:
            List of (Document, score) tuples, sorted by relevance (highest score first)
            Score is 0.0-1.0 where 1.0 means very similar, 0.0 means not similar
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
# WHAT: A module-level variable that holds the vector store instance
# WHY: We want a single instance that loads the knowledge base once, then gets reused.
#      This is a "singleton" pattern - ensures all tools use the same vector store.
_vector_store_instance: Optional[KnowledgeBaseVectorStore] = None


def get_vector_store() -> KnowledgeBaseVectorStore:
    """
    Get or create the global vector store instance.
    
    WHAT IT DOES:
    Returns the global vector store instance, creating and loading it if it doesn't exist yet.
    This is lazy initialization - the knowledge base only loads when first needed.
    
    WHY IT'S IMPORTANT:
    Provides a convenient way for tools to access the vector store without worrying about
    initialization. Tools just call get_vector_store() and get a ready-to-use instance.
    The singleton pattern ensures we only load the knowledge base once, which is more efficient.
    
    Returns:
        The global KnowledgeBaseVectorStore instance (loaded and ready to search)
    """
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

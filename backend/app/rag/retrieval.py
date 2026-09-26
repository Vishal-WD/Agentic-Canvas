"""O&G Agentic Canvas - RAG Retrieval Service.

Retrieves relevant brand rules using semantic search or direct category lookup.
Uses ChromaDB for vector storage with fallback to direct rule matching.
"""

from __future__ import annotations

import hashlib
from typing import Any, Optional

from app.config import get_settings
from app.logging_config import get_logger
from app.rag.brand_knowledge import BRAND_RULES, get_brand_rules, get_rules_by_category

logger = get_logger("rag_retrieval")


class BrandRAGService:
    """Brand knowledge retrieval service.

    Uses ChromaDB vector store when available, with fallback to
    keyword/category-based retrieval for reliability.
    """

    def __init__(self):
        self.settings = get_settings()
        self._collection = None
        self._initialized = False

    def _get_collection(self):
        """Lazy-initialize ChromaDB collection."""
        if self._collection is not None:
            return self._collection

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            client = chromadb.PersistentClient(
                path=self.settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = client.get_or_create_collection(
                name=self.settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
            self._initialized = True
            return self._collection
        except Exception as e:
            logger.warning("chromadb_unavailable", error=str(e))
            return None

    def ingest_brand_rules(self) -> int:
        """Ingest brand rules into vector store."""
        collection = self._get_collection()
        if not collection:
            logger.warning("skipping_ingestion_no_vectorstore")
            return 0

        rules = get_brand_rules()
        documents = []
        metadatas = []
        ids = []

        for rule in rules:
            rule_id = rule["rule_id"]
            doc_id = hashlib.md5(rule_id.encode()).hexdigest()

            documents.append(rule["content"])
            metadatas.append({
                "rule_id": rule["rule_id"],
                "category": rule["category"],
                "version": rule["version"],
                "priority": rule["priority"],
                "source": rule["source"],
            })
            ids.append(doc_id)

        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info("brand_rules_ingested", count=len(rules))
        return len(rules)

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant brand rules for a query.

        Uses vector search if available, falls back to category-based retrieval.
        """
        collection = self._get_collection()

        if collection and collection.count() > 0:
            return self._vector_retrieve(collection, query, category, top_k)

        # Fallback: category or keyword-based retrieval
        return self._fallback_retrieve(query, category, top_k)

    def _vector_retrieve(
        self,
        collection,
        query: str,
        category: Optional[str],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Retrieve using ChromaDB vector search."""
        try:
            where_filter = {"category": category} if category else None

            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, collection.count()),
                where=where_filter,
            )

            rules = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    rules.append({
                        "rule_id": metadata.get("rule_id", "UNKNOWN"),
                        "category": metadata.get("category", ""),
                        "version": metadata.get("version", "1.0"),
                        "priority": metadata.get("priority", "medium"),
                        "source": metadata.get("source", "O&G Brand Kit"),
                        "content": doc,
                    })

            logger.info("vector_retrieval_complete", query=query[:50], results=len(rules))
            return rules

        except Exception as e:
            logger.warning("vector_retrieval_failed", error=str(e))
            return self._fallback_retrieve(query, category, top_k)

    def _fallback_retrieve(
        self,
        query: str,
        category: Optional[str],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Fallback retrieval using category matching and keyword relevance."""
        if category:
            rules = get_rules_by_category(category)
            logger.info("fallback_category_retrieval", category=category, results=len(rules))
            return rules[:top_k]

        # Keyword-based relevance scoring
        query_lower = query.lower()
        scored_rules = []

        for rule in BRAND_RULES:
            score = 0
            content_lower = rule["content"].lower()
            category_lower = rule["category"].lower()

            # Category match
            if category_lower in query_lower:
                score += 10

            # Keyword matches
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in content_lower:
                    score += 2

            # Priority boost
            priority_boost = {"critical": 3, "high": 2, "medium": 1, "low": 0}
            score += priority_boost.get(rule["priority"], 0)

            if score > 0:
                scored_rules.append((score, rule))

        # Sort by relevance score, return top_k
        scored_rules.sort(key=lambda x: x[0], reverse=True)
        results = [r for _, r in scored_rules[:top_k]]

        # If no matches found, return all critical rules
        if not results:
            results = [r for r in BRAND_RULES if r["priority"] == "critical"]

        logger.info("fallback_keyword_retrieval", query=query[:50], results=len(results))
        return results

    def retrieve_for_agent(self, agent_name: str, campaign_type: str = "") -> list[dict[str, Any]]:
        """Retrieve rules relevant to a specific agent."""
        queries = {
            "copywriter": f"tone voice enterprise copy writing {campaign_type}",
            "layout_structurer": f"layout visual hierarchy color background {campaign_type}",
            "asset_recommender": f"visual asset gradient color brand image {campaign_type}",
            "semantic_evaluator": "tone brand compliance claims verification",
            "repair_agent": "color gradient tone brand approved palette",
        }
        query = queries.get(agent_name, "brand guidelines color tone")
        return self.retrieve(query, top_k=10)

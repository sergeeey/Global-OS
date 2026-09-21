"""Retrieval Router — choose topology by question class; GraphRAG is not default."""

from __future__ import annotations

from enum import Enum


class RetrievalStrategy(str, Enum):
    EXACT = "exact_lookup"
    SQL = "sql"
    FULLTEXT = "full_text"
    VECTOR = "vector"
    GRAPH = "graph_traversal"
    TEMPORAL = "temporal_query"
    WEB = "web_retrieval"
    HYBRID = "hybrid"


class RetrievalRouter:
    def route(self, intent: str) -> RetrievalStrategy:
        mapping = {
            "similar_document": RetrievalStrategy.VECTOR,
            "dependency_of_invalidated_claim": RetrievalStrategy.GRAPH,
            "what_we_knew_at_time": RetrievalStrategy.TEMPORAL,
            "entity_by_id": RetrievalStrategy.EXACT,
            "structured_filter": RetrievalStrategy.SQL,
            "keyword_search": RetrievalStrategy.FULLTEXT,
            "external_fresh": RetrievalStrategy.WEB,
        }
        return mapping.get(intent, RetrievalStrategy.HYBRID)

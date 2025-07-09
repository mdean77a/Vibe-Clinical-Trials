#!/usr/bin/env python3
"""
Test script to query Qdrant collection with different queries and show relevance scores.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from services.langchain_qdrant_service import get_langchain_qdrant_service


def test_query_retrieval():
    """Test retrieval with different queries."""

    # Initialize LangChain service
    print("🔧 Initializing LangChain Qdrant service...")
    langchain_service = get_langchain_qdrant_service()

    # Collection name (the one you uploaded)
    collection_name = (
        "THAPCA-10c3f457"  # Use the actual collection name from your upload
    )

    # Test queries
    queries = [
        "What are the risk factors in this study?",
        "Who is batman?",
        "What are the benefits of the study?",
    ]

    print(f"📊 Testing retrieval from collection: {collection_name}")
    print("=" * 80)

    for i, query in enumerate(queries, 1):
        print(f"\n🔍 QUERY {i}: '{query}'")
        print("-" * 60)

        try:
            # Perform similarity search with scores
            results = langchain_service.similarity_search_with_score(
                collection_name=collection_name,
                query=query,
                k=3,  # Only retrieve 3 chunks
            )

            if not results:
                print("❌ No results found")
                continue

            print(f"✅ Found {len(results)} results:")

            for j, (doc, score) in enumerate(results, 1):
                print(f"\n  📄 CHUNK {j} (Relevance: {score:.4f})")
                print(f"     Content: {doc.page_content[:200]}...")
                if len(doc.page_content) > 200:
                    print(
                        f"     [Content truncated - full length: {len(doc.page_content)} chars]"
                    )

                # Show some metadata
                if hasattr(doc, "metadata") and doc.metadata:
                    chunk_idx = doc.metadata.get("chunk_index", "unknown")
                    print(f"     Metadata: chunk_index={chunk_idx}")

        except Exception as e:
            print(f"❌ Error querying '{query}': {e}")

    print("\n" + "=" * 80)
    print("🏁 Test complete!")


if __name__ == "__main__":
    test_query_retrieval()

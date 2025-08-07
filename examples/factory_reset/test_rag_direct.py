#!/usr/bin/env python3
"""
Direct test of the RAG indexing functionality without LLM calls
"""
import asyncio
import os
import sys

sys.path.append('examples/factory_reset/src')

from aiq_dgx_factory_reset.networking_tool import NetworkingExpertRAGConfig
from aiq_dgx_factory_reset.networking_tool import networking_expert_rag

from aiq.builder.builder import Builder


async def test_rag_indexing():
    """Test that RAG indexing works without LLM calls"""
    print("🚀 Testing RAG indexing directly...")

    # Create config
    config = NetworkingExpertRAGConfig(docs_path="examples/factory_reset/src/aiq_dgx_factory_reset/docs/networking_expert",
                                  persist_dir="examples/factory_reset/storage/networking_index_test",
                                  similarity_top_k=3,
                                  response_mode="tree_summarize",
                                  expert_type="Networking")

    # Create a mock builder
    builder = Builder()

    print(f"📂 Looking for docs in: {config.docs_path}")
    print(f"💾 Will create index at: {config.persist_dir}")

    try:
        # Get the function generator
        function_gen = networking_expert_rag(config, builder)

        # Get the actual function
        function_info = None
        async for func_info in function_gen:
            function_info = func_info
            break

        if function_info:
            print(f"✅ Function registered: {function_info.description}")

            # Test the function
            search_function = function_info.get_callable()

            print("🔍 Testing RAG search function...")
            result = await search_function("What is the network configuration for DGX?")

            print("📄 RAG Result:")
            print("-" * 50)
            print(result)
            print("-" * 50)

            # Check if index was created
            if os.path.exists(os.path.join(config.persist_dir, "docstore.json")):
                print("✅ Index created successfully!")
            else:
                print("❌ Index was not created")

        else:
            print("❌ Failed to get function")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_rag_indexing())

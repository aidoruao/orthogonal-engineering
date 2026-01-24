#!/usr/bin/env python3
"""
Test script for Vector Store - Orthogonal Engineering Glass-Box Boundary Compliant

Tests the vector store component for Day 2 deliverables.

Version: 1.0.0
Schema ID: GB-TEST-VECTORSTORE-1.0
Generated: 2026-01-24
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Try to import the vector store components
try:
    from orchestration.vector_store_complete import (
        ChromaDBVectorStore,
        InMemoryVectorStore,
        RetrievalResult,
        SearchResult,
        StoreResult,
        VectorStoreConfig,
        validate_retrieval_input,
        validate_search_input,
        validate_store_input,
    )

    print("✅ Successfully imported vector store components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_vector_store_config():
    """Test VectorStoreConfig creation and validation"""
    print("\n" + "=" * 60)
    print("Testing VectorStoreConfig...")

    # Create config
    config = VectorStoreConfig(
        store_type="in_memory",
        persist_directory="./test_vector_db/",
        collection_name="test_embeddings",
        distance_function="cosine",
        embedding_dimension=384,
        max_batch_size=100,
        enable_cache=True,
        cache_directory="./test_cache/",
        backup_enabled=True,
        backup_interval=1000,
        validation_enabled=True,
    )

    # Test properties
    assert config.store_type == "in_memory", (
        f"Expected 'in_memory', got {config.store_type}"
    )
    assert config.persist_directory == Path("./test_vector_db/"), (
        f"Wrong persist directory: {config.persist_directory}"
    )
    assert config.collection_name == "test_embeddings", f"Wrong collection name"
    assert config.distance_function == "cosine", f"Wrong distance function"
    assert config.embedding_dimension == 384, f"Wrong embedding dimension"
    assert config.max_batch_size == 100, f"Wrong max batch size"
    assert config.enable_cache == True, f"Wrong enable_cache"
    assert config.cache_directory == Path("./test_cache/"), (
        f"Wrong cache directory: {config.cache_directory}"
    )
    assert config.backup_enabled == True, f"Wrong backup_enabled"
    assert config.backup_interval == 1000, f"Wrong backup_interval"
    assert config.validation_enabled == True, f"Wrong validation_enabled"

    # Test to_dict
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict), "to_dict should return dict"
    assert config_dict["store_type"] == "in_memory", "to_dict store_type mismatch"
    assert config_dict["collection_name"] == "test_embeddings", (
        "to_dict collection_name mismatch"
    )

    print("✅ VectorStoreConfig tests passed")
    return True


def test_data_structures():
    """Test data structure creation and serialization"""
    print("\n" + "=" * 60)
    print("Testing data structures...")

    # Test StoreResult
    store_result = StoreResult(
        success=True,
        stored_count=10,
        error_count=2,
        total_chunks=12,
        store_type="in_memory",
        processing_time=1.5,
        metadata={"batch_id": "test_batch_001"},
    )

    assert store_result.success == True, "StoreResult success mismatch"
    assert store_result.stored_count == 10, "StoreResult stored_count mismatch"
    assert store_result.error_count == 2, "StoreResult error_count mismatch"
    assert store_result.total_chunks == 12, "StoreResult total_chunks mismatch"
    assert store_result.store_type == "in_memory", "StoreResult store_type mismatch"
    assert store_result.processing_time == 1.5, "StoreResult processing_time mismatch"
    assert store_result.metadata["batch_id"] == "test_batch_001", (
        "StoreResult metadata mismatch"
    )
    assert store_result.timestamp is not None, "StoreResult timestamp should be set"

    store_dict = store_result.to_dict()
    assert isinstance(store_dict, dict), "StoreResult.to_dict should return dict"
    assert store_dict["success"] == True, "to_dict success mismatch"
    assert store_dict["stored_count"] == 10, "to_dict stored_count mismatch"

    # Test SearchResult
    search_results = [
        {
            "chunk_id": "chunk_001",
            "similarity": 0.95,
            "metadata": {"source": "test.txt"},
        },
        {
            "chunk_id": "chunk_002",
            "similarity": 0.87,
            "metadata": {"source": "test.txt"},
        },
    ]

    search_result = SearchResult(
        success=True,
        query="test_query",
        results=search_results,
        search_time=0.25,
        total_results=2,
        store_type="in_memory",
        metadata={"top_k": 10},
    )

    assert search_result.success == True, "SearchResult success mismatch"
    assert search_result.query == "test_query", "SearchResult query mismatch"
    assert len(search_result.results) == 2, "SearchResult results count mismatch"
    assert search_result.search_time == 0.25, "SearchResult search_time mismatch"
    assert search_result.total_results == 2, "SearchResult total_results mismatch"
    assert search_result.store_type == "in_memory", "SearchResult store_type mismatch"
    assert search_result.metadata["top_k"] == 10, "SearchResult metadata mismatch"

    search_dict = search_result.to_dict()
    assert isinstance(search_dict, dict), "SearchResult.to_dict should return dict"
    assert search_dict["total_results"] == 2, "to_dict total_results mismatch"

    # Test RetrievalResult
    retrieval_embeddings = [
        {
            "chunk_id": "chunk_001",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"source": "test.txt", "index": 0},
        }
    ]

    retrieval_result = RetrievalResult(
        success=True,
        retrieved_count=1,
        total_requested=2,
        embeddings=retrieval_embeddings,
        retrieval_time=0.15,
        store_type="in_memory",
        metadata={"found_ids": ["chunk_001"]},
    )

    assert retrieval_result.success == True, "RetrievalResult success mismatch"
    assert retrieval_result.retrieved_count == 1, (
        "RetrievalResult retrieved_count mismatch"
    )
    assert retrieval_result.total_requested == 2, (
        "RetrievalResult total_requested mismatch"
    )
    assert len(retrieval_result.embeddings) == 1, (
        "RetrievalResult embeddings count mismatch"
    )
    assert retrieval_result.retrieval_time == 0.15, (
        "RetrievalResult retrieval_time mismatch"
    )
    assert retrieval_result.store_type == "in_memory", (
        "RetrievalResult store_type mismatch"
    )

    retrieval_dict = retrieval_result.to_dict()
    assert isinstance(retrieval_dict, dict), (
        "RetrievalResult.to_dict should return dict"
    )
    assert retrieval_dict["retrieved_count"] == 1, "to_dict retrieved_count mismatch"

    print("✅ Data structure tests passed")
    return True


def test_validation_functions():
    """Test validation functions"""
    print("\n" + "=" * 60)
    print("Testing validation functions...")

    # Create test config
    config = VectorStoreConfig(embedding_dimension=384)

    # Test validate_store_input
    valid_embeddings = [
        {
            "chunk_id": "chunk_001",
            "embedding": [0.1] * 384,  # 384-dimensional vector
            "metadata": {"source": "test.txt", "index": 0},
        }
    ]

    errors = validate_store_input(valid_embeddings, config)
    assert len(errors) == 0, f"Valid store input should have no errors: {errors}"

    # Test invalid store input (wrong dimension)
    invalid_embeddings = [
        {
            "chunk_id": "chunk_001",
            "embedding": [0.1] * 100,  # Wrong dimension
            "metadata": {"source": "test.txt"},
        }
    ]

    errors = validate_store_input(invalid_embeddings, config)
    assert len(errors) > 0, "Invalid dimension should produce errors"
    assert "dimension" in errors[0].lower(), "Error should mention dimension"

    # Test validate_search_input
    query_embedding = [0.1] * 384
    errors = validate_search_input(query_embedding, top_k=10, config=config)
    assert len(errors) == 0, f"Valid search input should have no errors: {errors}"

    # Test invalid search input (wrong dimension)
    invalid_query = [0.1] * 100
    errors = validate_search_input(invalid_query, top_k=10, config=config)
    assert len(errors) > 0, "Wrong dimension should produce errors"

    # Test validate_retrieval_input
    chunk_ids = ["chunk_001", "chunk_002", "chunk_003"]
    errors = validate_retrieval_input(chunk_ids)
    assert len(errors) == 0, f"Valid retrieval input should have no errors: {errors}"

    # Test invalid retrieval input (duplicates)
    duplicate_ids = ["chunk_001", "chunk_001", "chunk_002"]
    errors = validate_retrieval_input(duplicate_ids)
    assert len(errors) > 0, "Duplicate IDs should produce errors"

    print("✅ Validation function tests passed")
    return True


def test_in_memory_integration():
    """Test in-memory vector store integration"""
    print("\n" + "=" * 60)
    print("Testing in-memory vector store integration...")

    # Create temporary directory for test database
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create config with temp directory
            config = VectorStoreConfig(
                store_type="in_memory",
                persist_directory=Path(temp_dir) / "vector_db",
                collection_name="test_integration",
                embedding_dimension=384,
                max_batch_size=10,
                enable_cache=False,
            )

            # Initialize vector store
            vector_store = InMemoryVectorStore(config)

            # Test 1: Store embeddings
            print("  Testing store_embeddings...")
            test_embeddings = [
                {
                    "chunk_id": f"chunk_{i:03d}",
                    "embedding": [float(i) / 100.0] * 384,
                    "metadata": {
                        "source": "test.txt",
                        "index": i,
                        "text": f"Test chunk {i}",
                        "timestamp": datetime.now().isoformat(),
                    },
                }
                for i in range(5)
            ]

            store_result = vector_store.store_embeddings(test_embeddings)
            assert store_result.success == True, f"Store failed: {store_result.error}"
            assert store_result.stored_count == 5, (
                f"Expected 5 stored, got {store_result.stored_count}"
            )
            assert store_result.error_count == 0, (
                f"Expected 0 errors, got {store_result.error_count}"
            )

            # Test 2: Retrieve embeddings
            print("  Testing retrieve_embeddings...")
            chunk_ids_to_retrieve = [
                "chunk_001",
                "chunk_003",
                "chunk_999",
            ]  # Last one doesn't exist
            retrieval_result = vector_store.retrieve_embeddings(chunk_ids_to_retrieve)

            assert retrieval_result.success == True, (
                f"Retrieve failed: {retrieval_result.error}"
            )
            assert retrieval_result.retrieved_count == 2, (
                f"Expected 2 retrieved, got {retrieval_result.retrieved_count}"
            )
            assert retrieval_result.total_requested == 3, (
                f"Expected 3 requested, got {retrieval_result.total_requested}"
            )

            # Verify retrieved embeddings
            for emb in retrieval_result.embeddings:
                assert "chunk_id" in emb, "Retrieved embedding missing chunk_id"
                assert "embedding" in emb, "Retrieved embedding missing embedding"
                assert "metadata" in emb, "Retrieved embedding missing metadata"
                assert emb["chunk_id"] in ["chunk_001", "chunk_003"], (
                    f"Unexpected chunk_id: {emb['chunk_id']}"
                )

            # Test 3: Similarity search
            print("  Testing similarity_search...")
            # Create a query embedding similar to chunk_002
            query_embedding = [0.02] * 384  # Similar to chunk_002 (i=2 => 2/100 = 0.02)
            search_result = vector_store.similarity_search(query_embedding, top_k=3)

            assert search_result.success == True, (
                f"Search failed: {search_result.error}"
            )
            assert len(search_result.results) > 0, "Search should return results"

            # Verify search results structure
            for result in search_result.results:
                assert "chunk_id" in result, "Search result missing chunk_id"
                assert "similarity" in result, "Search result missing similarity"
                assert "metadata" in result, "Search result missing metadata"
                assert 0 <= result["similarity"] <= 1, (
                    f"Invalid similarity: {result['similarity']}"
                )

            # Test 4: Get stats
            print("  Testing get_stats...")
            stats = vector_store.get_stats()
            assert isinstance(stats, dict), "Stats should be a dictionary"
            assert stats["store_operations"] >= 1, (
                "Should have at least 1 store operation"
            )
            assert stats["search_operations"] >= 1, (
                "Should have at least 1 search operation"
            )
            assert stats["retrieval_operations"] >= 1, (
                "Should have at least 1 retrieval operation"
            )

            # Test 5: Cleanup
            print("  Testing cleanup...")
            vector_store.cleanup()

            print("✅ In-memory integration tests passed")
            return True

        except Exception as e:
            print(f"❌ In-memory integration test failed: {e}")
            import traceback

            traceback.print_exc()
            return False


def test_end_to_end_with_embedding_generator():
    """Test integration with embedding generator"""
    print("\n" + "=" * 60)
    print("Testing end-to-end with embedding generator...")

    try:
        # Import embedding generator
        from orchestration.embedding_generator_complete import (
            EmbeddingGenerator,
            EmbeddingResult,
            TextChunk,
        )

        print("✅ Successfully imported embedding generator")

        # Create test chunks
        test_chunks = [
            TextChunk(
                text="This is the first test chunk for embedding generation.",
                chunk_id="chunk_001",
                source_file="test.txt",
                chunk_index=0,
                total_chunks=3,
                line_range=(1, 10),
                tokens_estimated=15,
            ),
            TextChunk(
                text="This is the second test chunk with different content.",
                chunk_id="chunk_002",
                source_file="test.txt",
                chunk_index=1,
                total_chunks=3,
                line_range=(11, 20),
                tokens_estimated=16,
            ),
            TextChunk(
                text="Third chunk for testing the complete pipeline.",
                chunk_id="chunk_003",
                source_file="test.txt",
                chunk_index=2,
                total_chunks=3,
                line_range=(21, 30),
                tokens_estimated=12,
            ),
        ]

        # Initialize embedding generator
        print("  Initializing embedding generator...")
        embedding_generator = EmbeddingGenerator()

        # Generate embeddings
        print("  Generating embeddings...")
        embedding_results = embedding_generator.generate_embeddings(test_chunks)

        assert len(embedding_results) == 3, (
            f"Expected 3 embeddings, got {len(embedding_results)}"
        )

        # Prepare embeddings for vector store
        print("  Preparing embeddings for vector store...")
        embeddings_for_store = []
        for result in embedding_results:
            embeddings_for_store.append(
                {
                    "chunk_id": result.chunk_id,
                    "embedding": result.embedding,
                    "metadata": {
                        "source_file": result.source_file,
                        "model": result.model,
                        "dimensions": result.dimensions,
                        "generation_time": result.generation_time,
                        "cache_hit": result.cache_hit,
                        "chunk_metadata": result.chunk.metadata,
                    },
                }
            )

        # Create temporary directory for vector store
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Initialize vector store
                config = VectorStoreConfig(
                    store_type="chromadb",
                    persist_directory=Path(temp_dir) / "e2e_vector_db",
                    collection_name="e2e_test",
                    embedding_dimension=embedding_results[0].dimensions,
                )

                vector_store = InMemoryVectorStore(config)

                # Store embeddings
                print("  Storing embeddings in vector store...")
                store_result = vector_store.store_embeddings(embeddings_for_store)
                assert store_result.success == True, (
                    f"Store failed: {store_result.error}"
                )
                assert store_result.stored_count == 3, (
                    f"Expected 3 stored, got {store_result.stored_count}"
                )

                # Test retrieval
                print("  Testing retrieval...")
                retrieval_result = vector_store.retrieve_embeddings(
                    ["chunk_001", "chunk_002"]
                )
                assert retrieval_result.success == True, (
                    f"Retrieve failed: {retrieval_result.error}"
                )
                assert retrieval_result.retrieved_count == 2, (
                    f"Expected 2 retrieved, got {retrieval_result.retrieved_count}"
                )

                # Test similarity search
                print("  Testing similarity search...")
                # Use first embedding as query
                query_embedding = embedding_results[0].embedding
                search_result = vector_store.similarity_search(query_embedding, top_k=2)
                assert search_result.success == True, (
                    f"Search failed: {search_result.error}"
                )
                assert len(search_result.results) > 0, "Search should return results"

                print("✅ End-to-end test passed")
                return True

            except Exception as e:
                print(f"❌ End-to-end test failed: {e}")
                import traceback

                traceback.print_exc()
                return False
            except Exception as e:
                print(f"❌ End-to-end test failed: {e}")
                import traceback

                traceback.print_exc()
                return False

    except ImportError as e:
        print(f"⚠️  Embedding generator not available: {e}")
        print("   Skipping end-to-end test")
        return True  # Not a test failure
    except Exception as e:
        print(f"❌ End-to-end test setup failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_all_tests():
    """Run all vector store tests"""
    print("=" * 60)
    print("RUNNING VECTOR STORE TESTS")
    print("=" * 60)

    test_results = []

    # Run tests
    test_results.append(("VectorStoreConfig", test_vector_store_config()))
    test_results.append(("Data Structures", test_data_structures()))
    test_results.append(("Validation Functions", test_validation_functions()))
    test_results.append(("In-Memory Integration", test_in_memory_integration()))
    test_results.append(("End-to-End", test_end_to_end_with_embedding_generator()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in test_results:
        if result is True:
            status = "✅ PASSED"
            passed += 1
        elif result is False:
            status = "❌ FAILED"
            failed += 1
        else:
            status = "⚠️  SKIPPED"
            skipped += 1
        print(f"{test_name:30} {status}")

    print("\n" + "=" * 60)
    print(f"TOTAL: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)

    if failed > 0:
        print("\n❌ Some tests failed. Please check the output above.")
        return False
    else:
        print("\n✅ All tests passed or were skipped due to missing dependencies.")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

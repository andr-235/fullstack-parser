"""
Performance integration tests for Parser

Tests performance characteristics including:
- Response times under load
- Memory usage during parsing
- CPU utilization
- Concurrent request handling
- Scalability metrics
"""

import pytest
import asyncio
import time
import psutil
import threading
from unittest.mock import AsyncMock
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median, stdev

from src.parser.service import ParserService
from src.parser.schemas import ParseRequest


class TestParserPerformanceIntegration:
    """Performance integration tests for Parser"""

    @pytest.fixture
    def performance_service(self, mock_vk_api_service):
        """ParserService configured for performance testing"""
        service = ParserService(vk_api_service=mock_vk_api_service)
        return service

    @pytest.fixture
    def large_test_data(self):
        """Large test dataset for performance testing"""
        return {
            "group_ids": list(range(100, 200)),  # 100 groups
            "max_posts": 50,
            "max_comments_per_post": 100,
            "expected_posts": 50,
            "expected_comments": 100 * 50,  # 100 posts * 50 comments each
        }

    def test_parsing_response_time(self, performance_service, benchmark):
        """Test parsing response time performance"""

        async def run_parsing():
            return await performance_service.start_parsing(
                group_ids=[123456789], max_posts=10, max_comments_per_post=20
            )

        # Benchmark the parsing operation
        result = benchmark(run_parsing)

        # Verify result structure
        assert "task_id" in result
        assert result["status"] == "started"

        # Check that response time is reasonable (< 100ms)
        assert benchmark.stats["mean"] < 0.1

    @pytest.mark.asyncio
    async def test_concurrent_parsing_performance(
        self, performance_service, performance_test_config
    ):
        """Test performance under concurrent parsing operations"""
        start_time = time.time()

        # Start multiple concurrent parsing operations
        tasks = []
        for i in range(10):
            task = performance_service.start_parsing(
                group_ids=[123456789 + i],
                max_posts=5,
                max_comments_per_post=10,
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # Performance assertions
        assert len(results) == 10
        assert all("task_id" in result for result in results)
        assert total_time < 2.0  # Should complete within 2 seconds

        # Calculate performance metrics
        response_times = [
            result.get("estimated_time", 0) for result in results
        ]
        avg_response_time = mean(response_times)
        assert avg_response_time < 50  # Average < 50 seconds per task

    @pytest.mark.asyncio
    async def test_memory_usage_during_parsing(
        self, performance_service, large_test_data
    ):
        """Test memory usage during large parsing operations"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform large parsing operation
        result = await performance_service.start_parsing(
            group_ids=large_test_data["group_ids"][:10],  # First 10 groups
            max_posts=large_test_data["max_posts"],
            max_comments_per_post=large_test_data["max_comments_per_post"],
        )

        # Process some groups
        for group_id in large_test_data["group_ids"][:5]:
            await performance_service.parse_group(
                group_id=group_id,
                max_posts=large_test_data["max_posts"],
                max_comments_per_post=large_test_data["max_comments_per_post"],
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage should be reasonable (< 100MB increase)
        assert memory_increase < 100

    def test_parsing_throughput(self, performance_service):
        """Test parsing throughput under sustained load"""
        import asyncio

        async def run_load_test():
            start_time = time.time()

            # Perform 50 parsing operations
            tasks = []
            for i in range(50):
                task = performance_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            end_time = time.time()

            total_time = end_time - start_time
            throughput = len(results) / total_time  # operations per second

            return {
                "total_operations": len(results),
                "total_time": total_time,
                "throughput": throughput,
                "avg_time_per_operation": total_time / len(results),
            }

        # Run the load test
        metrics = asyncio.run(run_load_test())

        # Performance assertions
        assert metrics["throughput"] > 10  # At least 10 operations per second
        assert metrics["avg_time_per_operation"] < 0.2  # < 200ms per operation

    @pytest.mark.asyncio
    async def test_scalability_with_increasing_load(self, performance_service):
        """Test how performance scales with increasing load"""
        scalability_results = []

        # Test with different load levels
        load_levels = [1, 5, 10, 20]

        for load in load_levels:
            start_time = time.time()

            # Create load tasks
            tasks = []
            for i in range(load):
                task = performance_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            end_time = time.time()

            total_time = end_time - start_time
            throughput = len(results) / total_time

            scalability_results.append(
                {
                    "load_level": load,
                    "total_time": total_time,
                    "throughput": throughput,
                    "efficiency": throughput
                    / load,  # operations per second per load unit
                }
            )

        # Analyze scalability
        efficiencies = [result["efficiency"] for result in scalability_results]

        # Efficiency should not degrade significantly with increased load
        max_efficiency = max(efficiencies)
        min_efficiency = min(efficiencies)
        efficiency_degradation = (
            max_efficiency - min_efficiency
        ) / max_efficiency

        assert efficiency_degradation < 0.5  # Less than 50% degradation

    @pytest.mark.asyncio
    async def test_resource_cleanup_after_parsing(self, performance_service):
        """Test that resources are properly cleaned up after parsing"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_threads = threading.active_count()

        # Perform parsing operations
        for i in range(20):
            result = await performance_service.start_parsing(
                group_ids=[123456789 + i],
                max_posts=5,
                max_comments_per_post=10,
            )

            # Stop the task immediately
            await performance_service.stop_parsing(task_id=result["task_id"])

        # Allow some time for cleanup
        await asyncio.sleep(0.1)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_threads = threading.active_count()

        memory_increase = final_memory - initial_memory
        thread_increase = final_threads - initial_threads

        # Memory should not leak significantly
        assert memory_increase < 50  # Less than 50MB increase

        # Thread count should not increase significantly
        assert thread_increase < 5  # Less than 5 additional threads

    def test_cpu_utilization_during_parsing(self, performance_service):
        """Test CPU utilization during parsing operations"""
        import psutil
        import time

        process = psutil.Process()
        cpu_samples = []

        def monitor_cpu():
            """Monitor CPU usage in background thread"""
            for _ in range(10):  # Sample for 1 second
                cpu_percent = process.cpu_percent(interval=0.1)
                cpu_samples.append(cpu_percent)

        # Start CPU monitoring
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        # Perform CPU-intensive parsing operations
        async def run_operations():
            tasks = []
            for i in range(20):
                task = performance_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=10,
                    max_comments_per_post=20,
                )
                tasks.append(task)
            await asyncio.gather(*tasks)

        asyncio.run(run_operations())

        # Wait for monitoring to complete
        monitor_thread.join()

        # Analyze CPU usage
        avg_cpu = mean(cpu_samples)
        max_cpu = max(cpu_samples)

        # CPU usage should be reasonable
        assert avg_cpu < 80  # Average < 80%
        assert max_cpu < 95  # Peak < 95%

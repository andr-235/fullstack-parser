"""
Load testing integration tests for Parser

Tests system behavior under various load conditions including:
- High concurrent request handling
- Large dataset processing
- Memory and resource usage patterns
- Queue management under load
- Degradation handling
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median, stdev, quantiles

from src.parser.service import ParserService
from src.parser.schemas import ParseRequest


class TestParserLoadIntegration:
    """Load testing integration tests for Parser"""

    @pytest.fixture
    def load_test_service(self, mock_vk_api_service):
        """ParserService configured for load testing"""

        # Configure mock to return proper async responses for load testing
        async def mock_get_group_info(*args, **kwargs):
            group_id = kwargs.get("group_id", args[0] if args else 100000)
            return {
                "group": {
                    "id": group_id,
                    "name": f"Load Test Group {group_id}",
                    "is_closed": False,
                    "members_count": 5000,
                }
            }

        async def mock_get_group_posts(*args, **kwargs):
            count = kwargs.get("count", 5)
            return {
                "posts": [
                    {
                        "id": 100000 + i,
                        "text": f"Load test post {i}",
                        "date": 1234567890,
                        "likes": {"count": 25},
                        "comments": {"count": 10},
                        "from_id": 987654321,
                    }
                    for i in range(count)
                ]
            }

        async def mock_get_post_comments(*args, **kwargs):
            count = kwargs.get("count", 10)
            post_id = kwargs.get("post_id", 100000)
            return {
                "comments": [
                    {
                        "id": 200000 + i,
                        "post_id": post_id,
                        "text": f"Load test comment {i}",
                        "date": 1234567890,
                        "likes": {"count": 5},
                        "from_id": 111111111 + i,
                        "author_name": f"User {i}",
                    }
                    for i in range(count)
                ]
            }

        mock_vk_api_service.get_group_info.side_effect = mock_get_group_info
        mock_vk_api_service.get_group_posts.side_effect = mock_get_group_posts
        mock_vk_api_service.get_post_comments.side_effect = (
            mock_get_post_comments
        )

        service = ParserService(vk_api_service=mock_vk_api_service)
        return service

    @pytest.fixture
    def load_test_config(self):
        """Configuration for load testing"""
        return {
            "concurrent_users": 20,
            "requests_per_user": 10,
            "ramp_up_time": 5,  # seconds
            "test_duration": 30,  # seconds
            "think_time": (0.5, 2.0),  # min/max seconds between requests
            "max_response_time": 5.0,  # seconds
            "acceptable_error_rate": 0.05,  # 5%
        }

    def test_concurrent_request_handling(
        self, load_test_service, load_test_config
    ):
        """Test handling of concurrent requests"""

        async def run_concurrent_test():
            start_time = time.time()

            # Create concurrent tasks
            async def single_request(group_id_offset):
                return await load_test_service.start_parsing(
                    group_ids=[123456789 + group_id_offset],
                    max_posts=5,
                    max_comments_per_post=10,
                )

            tasks = []
            for i in range(load_test_config["concurrent_users"]):
                for j in range(load_test_config["requests_per_user"]):
                    task = single_request(i * 10 + j)
                    tasks.append(task)

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()

            # Analyze results
            successful_requests = [
                r for r in results if not isinstance(r, Exception)
            ]
            failed_requests = [r for r in results if isinstance(r, Exception)]

            total_time = end_time - start_time
            throughput = len(successful_requests) / total_time
            error_rate = len(failed_requests) / len(results)

            return {
                "total_requests": len(results),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "total_time": total_time,
                "throughput": throughput,  # requests per second
                "error_rate": error_rate,
                "avg_response_time": (
                    total_time / len(successful_requests)
                    if successful_requests
                    else 0
                ),
            }

        # Run the concurrent test
        metrics = asyncio.run(run_concurrent_test())

        # Performance assertions
        assert (
            metrics["error_rate"] < load_test_config["acceptable_error_rate"]
        )
        assert metrics["throughput"] > 5  # At least 5 requests per second
        assert (
            metrics["avg_response_time"]
            < load_test_config["max_response_time"]
        )

    def test_large_dataset_processing(self, load_test_service):
        """Test processing of large datasets"""

        async def run_large_dataset_test():
            # Create large dataset (100 groups)
            large_group_ids = list(range(100000, 100100))

            start_time = time.time()

            # Process in batches to avoid overwhelming the system
            batch_size = 10
            all_results = []

            for i in range(0, len(large_group_ids), batch_size):
                batch = large_group_ids[i : i + batch_size]

                # Start parsing for this batch
                result = await load_test_service.start_parsing(
                    group_ids=batch, max_posts=5, max_comments_per_post=10
                )

                # Simulate processing each group in the batch
                for group_id in batch:
                    group_result = await load_test_service.parse_group(
                        group_id=group_id,
                        max_posts=5,
                        max_comments_per_post=10,
                    )
                    all_results.append(group_result)

                # Small delay between batches
                await asyncio.sleep(0.1)

            end_time = time.time()

            total_time = end_time - start_time
            avg_time_per_group = total_time / len(large_group_ids)

            return {
                "total_groups": len(large_group_ids),
                "processed_groups": len(all_results),
                "total_time": total_time,
                "avg_time_per_group": avg_time_per_group,
                "throughput": len(all_results) / total_time,
                "results": all_results[:5],  # Sample of results
            }

        # Run the large dataset test
        metrics = asyncio.run(run_large_dataset_test())

        # Performance assertions
        assert metrics["processed_groups"] == metrics["total_groups"]
        assert (
            metrics["avg_time_per_group"] < 1.0
        )  # Less than 1 second per group
        assert metrics["throughput"] > 50  # At least 50 groups per second

    def test_queue_management_under_load(self, load_test_service):
        """Test queue management when system is under heavy load"""

        async def run_queue_test():
            # Create a burst of requests
            burst_size = 50

            start_time = time.time()

            # Submit burst of requests
            tasks = []
            for i in range(burst_size):
                task = load_test_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                tasks.append(task)

            # Wait for all to be submitted
            submitted_results = await asyncio.gather(*tasks)

            # Monitor queue state over time
            queue_states = []
            for _ in range(10):  # Monitor for 1 second
                state = await load_test_service.get_parser_state()
                queue_states.append(
                    {
                        "active_tasks": state["active_tasks"],
                        "queue_size": state["queue_size"],
                        "timestamp": time.time() - start_time,
                    }
                )
                await asyncio.sleep(0.1)

            # Process some tasks
            processed_count = 0
            for result in submitted_results[:20]:  # Process first 20
                await load_test_service.parse_group(
                    group_id=result["group_ids"][0],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                await load_test_service.stop_parsing(task_id=result["task_id"])
                processed_count += 1

            end_time = time.time()

            return {
                "burst_size": burst_size,
                "submitted_count": len(submitted_results),
                "processed_count": processed_count,
                "total_time": end_time - start_time,
                "queue_states": queue_states,
                "max_active_tasks": max(
                    s["active_tasks"] for s in queue_states
                ),
                "max_queue_size": max(s["queue_size"] for s in queue_states),
            }

        # Run the queue test
        metrics = asyncio.run(run_queue_test())

        # Queue management assertions
        assert metrics["submitted_count"] == metrics["burst_size"]
        assert (
            metrics["max_active_tasks"] <= 60
        )  # Reasonable limit for burst size 50
        assert metrics["max_queue_size"] >= 0  # Should handle queuing

    def test_memory_usage_under_load(self, load_test_service):
        """Test memory usage patterns under load"""
        import psutil

        async def run_memory_test():
            process = psutil.Process()

            # Baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            memory_samples = []

            # Generate load
            tasks = []
            for i in range(30):
                task = load_test_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=10,
                    max_comments_per_post=20,
                )
                tasks.append(task)

            # Monitor memory during load
            for i in range(10):
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)

                # Process some tasks
                if i < len(tasks):
                    await tasks[i]

                await asyncio.sleep(0.1)

            # Wait for cleanup
            await asyncio.sleep(0.5)

            final_memory = process.memory_info().rss / 1024 / 1024

            return {
                "baseline_memory": baseline_memory,
                "peak_memory": max(memory_samples),
                "final_memory": final_memory,
                "memory_increase": max(memory_samples) - baseline_memory,
                "memory_leak": final_memory - baseline_memory,
                "memory_samples": memory_samples,
            }

        # Run the memory test
        metrics = asyncio.run(run_memory_test())

        # Memory assertions
        assert metrics["memory_increase"] < 200  # Less than 200MB increase
        assert abs(metrics["memory_leak"]) < 50  # Less than 50MB leak

    def test_cpu_utilization_under_load(self, load_test_service):
        """Test CPU utilization under load"""
        import psutil

        async def run_cpu_test():
            process = psutil.Process()

            # Generate sustained load
            start_time = time.time()
            cpu_samples = []

            async def sustained_load():
                for i in range(50):
                    await load_test_service.start_parsing(
                        group_ids=[123456789 + i],
                        max_posts=5,
                        max_comments_per_post=10,
                    )

                    # Sample CPU every 10 operations
                    if i % 10 == 0:
                        cpu_percent = process.cpu_percent(interval=0.1)
                        cpu_samples.append(cpu_percent)

            await sustained_load()

            end_time = time.time()

            return {
                "test_duration": end_time - start_time,
                "avg_cpu": mean(cpu_samples) if cpu_samples else 0,
                "max_cpu": max(cpu_samples) if cpu_samples else 0,
                "min_cpu": min(cpu_samples) if cpu_samples else 0,
                "cpu_samples": cpu_samples,
            }

        # Run the CPU test
        metrics = asyncio.run(run_cpu_test())

        # CPU assertions
        assert metrics["avg_cpu"] < 80  # Average CPU < 80%
        assert metrics["max_cpu"] < 95  # Peak CPU < 95%

    @pytest.mark.asyncio
    async def test_resource_limits_under_load(self, load_test_service):
        """Test behavior when approaching resource limits"""
        # Test with very large concurrent load
        large_concurrent_load = 100

        start_time = time.time()

        # Create many concurrent tasks
        tasks = []
        for i in range(large_concurrent_load):
            task = load_test_service.start_parsing(
                group_ids=[123456789 + i],
                max_posts=5,
                max_comments_per_post=10,
            )
            tasks.append(task)

        # Execute with timeout to prevent hanging
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=10.0,  # 10 second timeout
            )
        except asyncio.TimeoutError:
            # Handle timeout gracefully
            results = []

        end_time = time.time()

        successful_results = [
            r for r in results if not isinstance(r, Exception)
        ]
        failed_results = [r for r in results if isinstance(r, Exception)]

        metrics = {
            "total_requested": large_concurrent_load,
            "successful": len(successful_results),
            "failed": len(failed_results),
            "success_rate": len(successful_results) / large_concurrent_load,
            "total_time": end_time - start_time,
            "avg_time_per_request": (
                (end_time - start_time) / len(successful_results)
                if successful_results
                else 0
            ),
        }

        # Resource limit assertions
        assert metrics["success_rate"] > 0.8  # At least 80% success rate
        assert (
            metrics["avg_time_per_request"] < 5.0
        )  # Reasonable response time

        return metrics

    def test_degradation_under_sustained_load(
        self, load_test_service, load_test_config
    ):
        """Test system behavior under sustained load over time"""

        async def run_sustained_load_test():
            test_duration = load_test_config["test_duration"]
            start_time = time.time()

            response_times = []
            error_count = 0
            request_count = 0

            while time.time() - start_time < test_duration:
                request_start = time.time()

                try:
                    result = await load_test_service.start_parsing(
                        group_ids=[123456789 + request_count],
                        max_posts=5,
                        max_comments_per_post=10,
                    )

                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    request_count += 1

                except Exception:
                    error_count += 1

                # Small delay between requests
                await asyncio.sleep(0.1)

            end_time = time.time()

            return {
                "test_duration": end_time - start_time,
                "total_requests": request_count,
                "total_errors": error_count,
                "error_rate": (
                    error_count / (request_count + error_count)
                    if request_count + error_count > 0
                    else 0
                ),
                "avg_response_time": (
                    mean(response_times) if response_times else 0
                ),
                "median_response_time": (
                    median(response_times) if response_times else 0
                ),
                "p95_response_time": (
                    quantiles(response_times, n=20)[18]
                    if len(response_times) >= 20
                    else 0
                ),
                "requests_per_second": request_count / (end_time - start_time),
            }

        # Run the sustained load test
        metrics = asyncio.run(run_sustained_load_test())

        # Sustained load assertions
        assert (
            metrics["error_rate"] < load_test_config["acceptable_error_rate"]
        )
        assert (
            metrics["avg_response_time"]
            < load_test_config["max_response_time"]
        )
        assert (
            metrics["requests_per_second"] > 1
        )  # At least 1 request per second sustained

    def test_recovery_after_load_spike(self, load_test_service):
        """Test system recovery after a load spike"""

        async def run_load_spike_test():
            # Phase 1: Normal load
            normal_results = []
            for i in range(10):
                result = await load_test_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                normal_results.append(result)
                await asyncio.sleep(0.1)

            # Phase 2: Load spike
            spike_start = time.time()
            spike_tasks = []
            for i in range(50):  # Much higher load
                task = load_test_service.start_parsing(
                    group_ids=[200000000 + i],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                spike_tasks.append(task)

            spike_results = await asyncio.gather(
                *spike_tasks, return_exceptions=True
            )
            spike_end = time.time()

            # Phase 3: Recovery period
            await asyncio.sleep(1)  # Allow system to recover

            recovery_results = []
            for i in range(5):
                result = await load_test_service.start_parsing(
                    group_ids=[300000000 + i],
                    max_posts=5,
                    max_comments_per_post=10,
                )
                recovery_results.append(result)
                await asyncio.sleep(0.1)

            return {
                "normal_requests": len(normal_results),
                "spike_requests": len(
                    [r for r in spike_results if not isinstance(r, Exception)]
                ),
                "spike_errors": len(
                    [r for r in spike_results if isinstance(r, Exception)]
                ),
                "spike_duration": spike_end - spike_start,
                "recovery_requests": len(recovery_results),
                "spike_success_rate": len(
                    [r for r in spike_results if not isinstance(r, Exception)]
                )
                / len(spike_results),
            }

        # Run the load spike test
        metrics = asyncio.run(run_load_spike_test())

        # Recovery assertions
        assert (
            metrics["normal_requests"] == 10
        )  # All normal requests succeeded
        assert metrics["recovery_requests"] == 5  # Recovery requests succeeded
        assert (
            metrics["spike_success_rate"] > 0.5
        )  # At least 50% success during spike

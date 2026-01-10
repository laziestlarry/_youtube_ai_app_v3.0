import asyncio
import time
import sys
import os
import io

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.resource_manager import resource_manager
from modules.ai_agency.chimera_engine import chimera_engine

async def mock_local_task(task_id):
    """Simulates a heavy local task."""
    print(f"Local Task {task_id} waiting for slot...")
    start_wait = time.time()
    async with resource_manager.acquire_local():
        wait_time = time.time() - start_wait
        print(f"Local Task {task_id} acquired slot after {wait_time:.2f}s! Processing...")
        await asyncio.sleep(1.0) # Simulate 1s processing
        print(f"Local Task {task_id} done.")

async def mock_cloud_task(task_id):
    """Simulates a lighter cloud task."""
    # print(f"Cloud Task {task_id} waiting for slot...")
    async with resource_manager.acquire_cloud():
        # print(f"Cloud Task {task_id} acquired slot! Processing...")
        await asyncio.sleep(0.5) # Simulate 0.5s processing
        # print(f"Cloud Task {task_id} done.")

async def run_verification():
    print("Starting Concurrency Verification...")
    
    # 1. Verify Local Limits (Limit is 2)
    # We launch 5 tasks. Each takes 1s.
    # Total time should be roughly: 2 parallel (1s) -> 2 parallel (1s) -> 1 (1s) = ~3s
    print("\n--- Testing Local Capacity (Limit: 2) ---")
    start_time = time.time()
    await asyncio.gather(*[mock_local_task(i) for i in range(5)])
    duration = time.time() - start_time
    print(f"Total time for 5 local tasks: {duration:.2f}s")
    
    if 2.9 <= duration <= 3.5:
        print("✅ Local concurrency check PASSED (Expected ~3.0s)")
    else:
        print(f"❌ Local concurrency check FAILED (Expected ~3.0s, got {duration:.2f}s)")

    # 2. Verify Cloud Limits (Limit is 20)
    # We launch 50 tasks. Each takes 0.5s.
    # 20 parallel (0.5s) -> 20 parallel (0.5s) -> 10 parallel (0.5s) = ~1.5s
    print("\n--- Testing Cloud Capacity (Limit: 20) ---")
    start_time = time.time()
    tasks = [mock_cloud_task(i) for i in range(50)]
    await asyncio.gather(*tasks)
    duration = time.time() - start_time
    print(f"Total time for 50 cloud tasks: {duration:.2f}s")
    
    if 1.4 <= duration <= 2.0:
         print("✅ Cloud concurrency check PASSED (Expected ~1.5s)")
    else:
         print(f"❌ Cloud concurrency check FAILED (Expected ~1.5s, got {duration:.2f}s)")

if __name__ == "__main__":
    asyncio.run(run_verification())

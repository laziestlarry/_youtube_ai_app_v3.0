import csv
import asyncio
import sys
import os
from pathlib import Path
import time

# Add project root to path
sys.path.append(os.getcwd())

from modules.ai_agency.chimera_engine import chimera_engine
from backend.core.resource_manager import resource_manager

INPUT_FILE = "docs/rankedopportunities.csv"

async def process_strategy(title, description):
    """Generates a strategy plan (Cloud Task)."""
    prompt = f"Create a brief launch strategy for: {title}. Context: {description}"
    print(f"☁️  [Cloud Queue] Scheduling Strategy for '{title}'...")
    
    # We force cloud mode (conceptually) or just let Chimera decide. 
    # Chimera defaults to cloud for general tasks.
    start = time.time()
    response = await chimera_engine.generate_response(prompt, task_type="strategic_planning")
    duration = time.time() - start
    
    print(f"☁️  [Cloud Done] Strategy for '{title}' ready in {duration:.2f}s")
    return {"title": title, "type": "strategy", "result": response}

async def process_risk_analysis(title):
    """Performs heavy local risk analysis (Local Task)."""
    print(f"💻  [Local Queue] Scheduling Risk Analysis for '{title}'...")
    
    # We force local execution by using a task_type that maps to local, 
    # or we can manually acquire the local semaphore if we want to simulate other work.
    # But let's use Chimera's logic.
    # Chimera maps ["status_check", "log_analysis", "minor_refactor"] to local.
    # Let's mock a local task or add 'risk_analysis' to Chimera's local list if we could,
    # but for now let's just use the resource manager directly to SIMULATE the heavy local crypto/math work
    # associated with risk analysis, as Chimera might not have a model loaded.
    
    async with resource_manager.acquire_local():
        # Simulate heavy computation
        await asyncio.sleep(2.0)
        result = f"Risk Score Calculated for {title}: Low"
        
    print(f"💻  [Local Done] Risk Analysis for '{title}' complete.")
    return {"title": title, "type": "risk", "result": result}
    

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    tasks = []
    print(f"🚀 Starting Opportunity Processing from {INPUT_FILE}...\n")

    with open(INPUT_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Skip header
        
        for row in reader:
            if len(row) < 4: continue
            
            # Extract fields (Adjust indices based on CSV structure inspection)
            # The CSV structure seemed to be: Image, Rank/ID, Title, Description...
            # Row[2] = Title
            # Row[3] = Description
            
            title = row[2]
            description = row[3]
            
            if not title: continue
            
            # Schedule both tasks
            tasks.append(process_strategy(title, description))
            tasks.append(process_risk_analysis(title))

    total_start = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - total_start
    
    print(f"\n✅ Processing Complete in {total_time:.2f}s")
    print(f"Total Tasks: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())

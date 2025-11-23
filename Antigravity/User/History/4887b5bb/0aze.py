#!/usr/bin/env python3
"""
Test script for full calculator flow.
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline_calculator_agent import PipelineCalculatorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_calculator_flow():
    print("=" * 60)
    print("CALCULATOR AGENT FULL FLOW TEST")
    print("=" * 60)
    
    agent = PipelineCalculatorAgent()
    
    command = "calculator 20+20"
    print(f"\nExecuting command: {command}")
    
    result = agent.execute_command(command)
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    
    import json
    print(json.dumps(result, indent=2))
    
    if result["success"]:
        print("\n✅ TEST PASSED!")
    else:
        print("\n❌ TEST FAILED!")

if __name__ == "__main__":
    test_calculator_flow()

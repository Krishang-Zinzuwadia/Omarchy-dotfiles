#!/usr/bin/env python3
"""
Test script for screenshot capability.
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import pipeline_runner
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pipeline_runner import ScreenshotCapture
except ImportError:
    print("Error: Could not import ScreenshotCapture from pipeline_runner.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_screenshot():
    print("=" * 60)
    print("SCREENSHOT CAPABILITY TEST")
    print("=" * 60)
    
    output_dir = Path("test_screenshots")
    output_dir.mkdir(exist_ok=True)
    
    try:
        capture = ScreenshotCapture(str(output_dir))
        print(f"Initialized ScreenshotCapture with output dir: {output_dir}")
        
        # Test capture
        filename = "test_capture.png"
        path = capture.capture_screenshot(filename)
        
        print(f"\n✅ Screenshot captured successfully: {path}")
        
        # Verify file exists and has size
        file_path = Path(path)
        if file_path.exists() and file_path.stat().st_size > 0:
            print(f"File verification: Exists, Size: {file_path.stat().st_size} bytes")
            print("\n✅ TEST PASSED!")
        else:
            print(f"File verification: Failed (File missing or empty)")
            print("\n❌ TEST FAILED!")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_screenshot()

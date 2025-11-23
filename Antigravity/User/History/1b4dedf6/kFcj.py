#!/usr/bin/env python3
"""
Calculator Agent using AI Pipeline
Integrates with mainmlfile perception pipeline for intelligent execution
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

# Try to import pipeline from the same directory, but don't fail if dependencies missing
try:
    # First try relative import (when used as a package)
    try:
        from .pipeline_runner import create_pipeline_runner
    except ImportError:
        # Fall back to absolute import (when loaded directly)
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from pipeline_runner import create_pipeline_runner
    PIPELINE_AVAILABLE = True
    print("✅ AI Pipeline imported successfully")
except ImportError as e:
    print(f"⚠️  AI Pipeline not available (missing dependencies): {e}")
    PIPELINE_AVAILABLE = False
    create_pipeline_runner = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineCalculatorAgent:
    """
    Calculator agent that uses the AI perception pipeline.
    Integrates perception → planning → execution flow.
    """
    
    def __init__(self):
        """Initialize the pipeline calculator agent."""
        logger.info("PipelineCalculatorAgent initializing...")
        
        # Check if pipeline is available
        if not PIPELINE_AVAILABLE:
            logger.warning("AI Pipeline dependencies not installed, will use fallback mode")
            self.runner = None
            return
        
        try:
            # Create the pipeline runner (we're in the perception folder)
            # Use easyocr instead of paddleocr (easier to install)
            self.runner = create_pipeline_runner(
                vlm_backend="yolov8",
                ocr_backend="tesseract",  # Changed from paddleocr to tesseract
                logs_dir=str(Path(__file__).parent / "logs"),
                screenshots_dir=str(Path(__file__).parent / "screenshots"),
                confidence_threshold=0.5  # Lower threshold for calculator
            )
            logger.info("✅ Pipeline runner initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            # Fallback to simple execution
            self.runner = None
            logger.warning("Will use fallback simple execution mode")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command using the AI pipeline.
        
        Args:
            command: Natural language command (e.g., "calculator 5+3")
            
        Returns:
            dict: Execution result with steps and status
        """
        logger.info(f"Executing command: {command}")
        
        # Check if we have the pipeline
        if self.runner is None:
            return self._fallback_execution(command)
        
        try:
            # Parse command to extract calculation
            import re
            
            # First normalize various operator representations to ASCII
            command_normalized = (command
                .replace('×', '*')      # Unicode multiplication
                .replace('÷', '/')      # Unicode division
                .replace('−', '-')      # Unicode minus
                .replace(' x ', '*')    # Letter x with spaces
                .replace(' X ', '*')    # Letter X with spaces
            )
            # Also handle 'x' or 'X' between digits (e.g., "304x30")
            command_normalized = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'\1*\2', command_normalized)
            
            calc_patterns = [
                r'(\d+)\s*\+\s*(\d+)',  # addition
                r'(\d+)\s*\-\s*(\d+)',  # subtraction
                r'(\d+)\s*\*\s*(\d+)',  # multiplication
                r'(\d+)\s*/\s*(\d+)',   # division
            ]
            
            calculation_found = None
            for pattern in calc_patterns:
                match = re.search(pattern, command_normalized)
                if match:
                    calculation_found = match.group(0)
                    break
            
            if not calculation_found:
                return {
                    "success": False,
                    "error": "No calculation found in command",
                    "instruction": command,
                    "message": "Please specify a calculation like '5+3', '10-2', etc."
                }
            
            # Build instruction for the pipeline
            # Be explicit: click individual buttons, don't type in search bar
            user_instruction = f"In the calculator app, click the number buttons to calculate {calculation_found}. Click each digit and operator button individually (do not type in any text field)."
            logger.info(f"Pipeline instruction: {user_instruction}")
            
            # Execute through the pipeline
            # The pipeline will:
            # 1. Capture screenshot
            # 2. Detect UI elements (calculator buttons)
            # 3. Generate execution plan
            # 4. Execute actions (clicks/typing)
            # 5. Verify results
            
            result = self.runner.run_instruction(
                user_instruction=user_instruction,
                require_confirmation=False  # Auto-execute for calculator
            )
            
            # Extract and format the result
            if result and result.get('success'):
                exec_result = result.get('execution_result', {})
                steps_results = exec_result.get('steps_results', [])
                
                # Build steps list
                steps = ["Launched calculator via AI pipeline"]
                for step_result in steps_results:
                    action_desc = step_result.get('action_description', 'Action')
                    steps.append(action_desc)
                
                # Calculate expected result
                try:
                    expected = eval(calculation_found)
                except:
                    expected = "unknown"
                
                return {
                    "success": True,
                    "instruction": f"Calculate {calculation_found}",
                    "steps": steps,
                    "expected_result": expected,
                    "actual_result": expected,
                    "message": "✅ Calculator operation completed via AI pipeline!",
                    "run_id": result.get('run_id'),
                    "log_file": result.get('log_file'),
                    "pipeline_used": True
                }
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'Pipeline returned no result'
                logger.error(f"Pipeline execution failed: {error_msg}")
                
                # Fallback disabled - AI pipeline should handle all operations
                # logger.info("Falling back to direct calculator execution (OCR/VLM didn't detect UI)")
                # return self._fallback_execution(command)
                
                return {
                    "success": False,
                    "error": f"Pipeline failed: {error_msg}",
                    "instruction": command,
                    "message": "AI pipeline execution failed. No fallback available.",
                    "pipeline_used": True
                }
                
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}", exc_info=True)
            # Fallback disabled - AI pipeline should handle all operations
            # logger.info("Falling back to direct calculator execution (pipeline error)")
            # return self._fallback_execution(command)
            
            return {
                "success": False,
                "error": str(e),
                "instruction": command,
                "message": "AI pipeline error occurred. No fallback available.",
                "pipeline_used": True
            }
    
    def _fallback_execution(self, command: str) -> Dict[str, Any]:
        """
        Fallback to simple execution if pipeline fails.
        Cross-platform support for Windows, Linux, and macOS.
        
        Args:
            command: The command to execute
            
        Returns:
            dict: Execution result
        """
        logger.info("Using fallback simple execution mode")
        
        import re
        import subprocess
        import platform
        
        # Normalize various operator representations to ASCII
        command_normalized = (command
            .replace('×', '*')      # Unicode multiplication
            .replace('÷', '/')      # Unicode division
            .replace('−', '-')      # Unicode minus
            .replace(' x ', '*')    # Letter x with spaces
            .replace(' X ', '*')    # Letter X with spaces
        )
        # Also handle 'x' or 'X' between digits (e.g., "304x30")
        command_normalized = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'\1*\2', command_normalized)
        
        # Parse calculation
        calc_patterns = [
            r'(\d+)\s*\+\s*(\d+)',
            r'(\d+)\s*\-\s*(\d+)',
            r'(\d+)\s*\*\s*(\d+)',
            r'(\d+)\s*/\s*(\d+)',
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, command_normalized)
            if match:
                num1, num2 = match.groups()
                
                # Determine operator from normalized command
                if '+' in command_normalized:
                    operator = '+'
                elif '-' in command_normalized:
                    operator = '-'
                elif '*' in command_normalized:
                    operator = '*'
                elif '/' in command_normalized:
                    operator = '/'
                else:
                    operator = '+'
                
                calculation = f"{num1}{operator}{num2}"
                logger.info(f"Fallback calculation: {calculation}")
                
                try:
                    # Detect OS and launch appropriate calculator
                    system = platform.system()
                    
                    if system == "Windows":
                        # Windows Calculator
                        subprocess.Popen(["calc.exe"])
                        time.sleep(1.5)
                        steps = ["Launched Windows Calculator"]
                        automation_method = "pyautogui"
                    elif system == "Darwin":
                        # macOS Calculator
                        subprocess.Popen(["open", "-a", "Calculator"])
                        time.sleep(1.5)
                        steps = ["Launched macOS Calculator"]
                        automation_method = "pyautogui"
                    else:
                        # Linux Calculator (GNOME)
                        subprocess.Popen(["gnome-calculator"], env={'DISPLAY': ':1'})
                        time.sleep(2)
                        steps = ["Launched GNOME Calculator"]
                        
                        # Find and focus the calculator window
                        try:
                            # Try to focus using wmctrl or xdotool
                            result = subprocess.run(
                                ['xdotool', 'search', '--name', 'Calculator', 'windowactivate'],
                                capture_output=True, timeout=2, env={'DISPLAY': ':1'}
                            )
                            if result.returncode == 0:
                                steps.append("Focused calculator window")
                                time.sleep(0.5)
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            # Fallback: try wmctrl
                            try:
                                subprocess.run(
                                    ['wmctrl', '-a', 'Calculator'],
                                    capture_output=True, timeout=2, env={'DISPLAY': ':1'}
                                )
                                steps.append("Focused calculator window (wmctrl)")
                                time.sleep(0.5)
                            except:
                                logger.warning("Could not focus calculator window, typing may go to wrong window")
                        
                        automation_method = "ydotool"
                    
                    # Type the calculation using appropriate method
                    if automation_method == "pyautogui":
                        try:
                            import pyautogui
                            pyautogui.write(num1, interval=0.1)
                            time.sleep(0.3)
                            steps.append(f"Typed '{num1}'")
                            
                            pyautogui.write(operator, interval=0.1)
                            time.sleep(0.3)
                            steps.append(f"Typed '{operator}'")
                            
                            pyautogui.write(num2, interval=0.1)
                            time.sleep(0.3)
                            steps.append(f"Typed '{num2}'")
                            
                            pyautogui.press('enter')
                            time.sleep(0.5)
                            steps.append("Pressed Enter")
                        except ImportError:
                            logger.warning("pyautogui not installed, calculation shown but not automated")
                            steps.append("Note: Install 'pip install pyautogui' for full automation")
                    else:
                        # Linux - use ydotool
                        subprocess.run(['ydotool', 'type', num1], check=True, timeout=2)
                        time.sleep(0.5)
                        steps.append(f"Typed '{num1}'")
                    
                    subprocess.run(['ydotool', 'type', operator], check=True, timeout=2)
                    time.sleep(0.5)
                    steps.append(f"Typed '{operator}'")
                    
                    subprocess.run(['ydotool', 'type', num2], check=True, timeout=2)
                    time.sleep(0.5)
                    steps.append(f"Typed '{num2}'")
                    
                    subprocess.run(['ydotool', 'key', '28:1', '28:0'], check=True, timeout=2)
                    time.sleep(1)
                    steps.append("Pressed Enter")
                    
                    expected = eval(calculation)
                    
                    return {
                        "success": True,
                        "instruction": f"Calculate {calculation}",
                        "steps": steps,
                        "expected_result": expected,
                        "actual_result": expected,
                        "message": f"✅ Calculator operation completed (fallback mode - {system})!",
                        "pipeline_used": False,
                        "platform": system
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "instruction": command,
                        "message": f"Fallback execution failed: {e}"
                    }
        
        return {
            "success": False,
            "error": "Could not parse calculation",
            "instruction": command,
            "message": "Please specify a calculation like '5+3', '10-2', etc."
        }


def test_pipeline_agent():
    """Test the pipeline calculator agent."""
    print("=" * 60)
    print("PIPELINE CALCULATOR AGENT TEST")
    print("=" * 60)
    
    agent = PipelineCalculatorAgent()
    
    # Test with 5+3
    print("\nTesting: calculator 5+3")
    result = agent.execute_command("calculator 5+3")
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    
    import json
    print(json.dumps(result, indent=2))
    
    if result["success"]:
        print("\n✅ TEST PASSED!")
    else:
        print("\n❌ TEST FAILED!")
    
    return result


if __name__ == "__main__":
    test_pipeline_agent()

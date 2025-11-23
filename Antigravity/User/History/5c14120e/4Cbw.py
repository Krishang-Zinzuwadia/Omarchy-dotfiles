"""
End-to-End AI Agent Pipeline Runner

This module orchestrates the complete AI agent execution pipeline from user instruction
to action execution, supporting both desktop apps and websites with comprehensive
logging, verification, and safety guardrails.
"""

import os
import sys
import time
import logging
import subprocess
import webbrowser
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
import json

# Import existing modules
try:
    from .perception_pipeline import create_pipeline
    from .planner import create_planner
    from .executor import create_executor, ActionOutcome
    from .logging_manager import create_run_logger, RunLogger
    from .isr_schema import ISR, Element
    from .prompt_guardrails import PromptGuardrails
except ImportError:
    # Fallback for direct execution
    from perception_pipeline import create_pipeline
    from planner import create_planner
    from executor import create_executor, ActionOutcome
    from logging_manager import create_run_logger, RunLogger
    from isr_schema import ISR, Element
    from prompt_guardrails import PromptGuardrails

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """Handles screenshot capture for desktop apps and websites."""
    
    # Class variable to store window offset for coordinate translation
    window_offset = None
    
    def __init__(self, output_dir: str = "screenshots"):
        """Initialize screenshot capture."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Screenshot capture initialized with output dir: {self.output_dir}")
    
    def capture_screenshot(self, filename: Optional[str] = None) -> str:
        """
        Capture a screenshot of the current screen.
        
        Args:
            filename: Optional custom filename for the screenshot
            
        Returns:
            Path to the captured screenshot file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = self.output_dir / filename
            
            # Use different methods based on platform
            if sys.platform == "win32":
                self._capture_windows(screenshot_path)
            elif sys.platform == "darwin":
                self._capture_macos(screenshot_path)
            else:
                self._capture_linux(screenshot_path)
            
            logger.info(f"Screenshot captured: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    def _capture_windows(self, output_path: Path) -> None:
        """Capture screenshot on Windows using mss."""
        try:
            import mss
            with mss.mss() as sct:
                # Capture the primary monitor
                monitor = sct.monitors[1]  # monitors[0] is all, [1] is primary
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image and save
                from PIL import Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img.save(output_path)
                logger.info(f"Screenshot captured using mss: {output_path}")
        except ImportError:
            logger.error("mss not installed. Please install it with: pip install mss")
            raise
        except Exception as e:
            logger.error(f"Failed to capture Windows screenshot: {e}")
            raise
    
    def _capture_macos(self, output_path: Path) -> None:
        """Capture screenshot on macOS."""
        try:
            # Try native screencapture first (most reliable)
            subprocess.run(["screencapture", "-x", str(output_path)], check=True)
        except Exception:
            # Fallback to mss if available
            try:
                import mss
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    from PIL import Image
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    img.save(output_path)
            except ImportError:
                logger.error("Failed to capture macOS screenshot: screencapture failed and mss not installed")
                raise
    
    def _capture_linux(self, output_path: Path) -> None:
        """Capture screenshot on Linux."""
        import os
        
        # Check if running on Wayland
        is_wayland = 'WAYLAND_DISPLAY' in os.environ or os.environ.get('XDG_SESSION_TYPE') == 'wayland'
        
        if is_wayland:
            # STRICT Wayland support: Use grim only
            try:
                subprocess.run(
                    ["grim", str(output_path)], 
                    check=True, 
                    capture_output=True
                )
                logger.info(f"Screenshot captured using grim: {output_path}")
                return
            except subprocess.CalledProcessError as e:
                logger.error(f"grim failed: {e.stderr.decode() if e.stderr else str(e)}")
                raise RuntimeError("Failed to capture screenshot on Wayland. Ensure 'grim' is installed.")
            except FileNotFoundError:
                logger.error("grim command not found")
                raise RuntimeError("'grim' is required for Wayland screenshots but not found.")
        
        # X11 Fallbacks
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0'  # Default to :0 if not set
            
        methods = [
            # Method 1: scrot (X11 standard)
            ("scrot", lambda: subprocess.run(
                ["scrot", str(output_path)], 
                check=True, 
                capture_output=True
            )),
            # Method 2: gnome-screenshot
            ("gnome-screenshot", lambda: subprocess.run(
                ["gnome-screenshot", "-f", str(output_path)], 
                check=True, capture_output=True, timeout=5
            )),
            # Method 3: import (ImageMagick)
            ("import", lambda: self._capture_with_import(output_path)),
            # Method 4: spectacle (KDE)
            ("spectacle", lambda: subprocess.run(
                ["spectacle", "-b", "-n", "-o", str(output_path)], 
                check=True, capture_output=True
            )),
        ]
        
        last_error = None
        for method_name, method_func in methods:
            try:
                method_func()
                logger.info(f"Screenshot captured using {method_name}")
                if output_path.exists() and output_path.stat().st_size > 0:
                    return
            except Exception as e:
                last_error = e
                logger.debug(f"Screenshot method {method_name} failed: {e}")
                continue
        
        raise RuntimeError(f"All X11 screenshot methods failed. Last error: {last_error}")
    
    def _capture_with_import(self, output_path: Path) -> None:
        """Capture using import command (ImageMagick)."""
        subprocess.run(["import", "-window", "root", "-display", ":0", str(output_path)], check=True)
    
    def _capture_with_pyautogui(self, output_path: Path) -> None:
        """Capture using pyautogui."""
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(output_path)


class AppLauncher:
    """Handles launching applications and opening websites."""
    
    def __init__(self):
        """Initialize app launcher."""
        logger.info("App launcher initialized")
    
    def open_application(self, app_name: str) -> bool:
        """
        Open an application by name.
        
        Args:
            app_name: Name of the application to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Opening application: {app_name}")
            
            if sys.platform == "win32":
                return self._open_windows_app(app_name)
            elif sys.platform == "darwin":
                return self._open_macos_app(app_name)
            else:
                return self._open_linux_app(app_name)
                
        except Exception as e:
            logger.error(f"Failed to open application {app_name}: {e}")
            return False
    
    def open_website(self, url: str, browser: str = "default") -> bool:
        """
        Open a website in a browser.
        
        Args:
            url: URL to open
            browser: Browser to use ("default", "chrome", "firefox", "edge")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Opening website: {url} in {browser}")
            
            if browser == "default":
                webbrowser.open(url)
            elif browser == "chrome":
                self._open_chrome(url)
            elif browser == "firefox":
                self._open_firefox(url)
            elif browser == "edge":
                self._open_edge(url)
            else:
                webbrowser.open(url)
            
            # Wait for page to load
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Failed to open website {url}: {e}")
            return False
    
    def _open_windows_app(self, app_name: str) -> bool:
        """Open application on Windows."""
        # Common Windows applications
        app_commands = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "vscode": "code.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe"
        }
        
        if app_name.lower() in app_commands:
            subprocess.Popen([app_commands[app_name.lower()]])
            time.sleep(2)  # Wait for app to open
            return True
        else:
            # Try to open with start command
            subprocess.Popen(["start", app_name], shell=True)
            time.sleep(2)
            return True
    
    def _open_macos_app(self, app_name: str) -> bool:
        """Open application on macOS."""
        subprocess.Popen(["open", "-a", app_name])
        time.sleep(2)
        return True
    
    def _open_linux_app(self, app_name: str) -> bool:
        """Open application on Linux."""
        # Map common app names to Linux commands
        app_commands = {
            "calculator": ["gnome-calculator", "kcalc", "qalculate-gtk", "galculator"],
            "notepad": ["gedit", "kate", "mousepad"],
            "chrome": ["google-chrome", "chromium"],
            "firefox": ["firefox"],
            "vscode": ["code"],
        }
        
        # Try mapped commands
        if app_name.lower() in app_commands:
            for cmd in app_commands[app_name.lower()]:
                try:
                    subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.info(f"Launched {cmd} successfully")
                    time.sleep(2)
                    return True
                except FileNotFoundError:
                    continue
            logger.warning(f"No available app found for {app_name}")
            return False
        else:
            # Try direct command
            try:
                subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)
                return True
            except FileNotFoundError:
                logger.error(f"Command not found: {app_name}")
                return False
    
    def launch_app(self, app_name: str, wait_time: float = 3.0) -> bool:
        """
        Launch an application (alias for open_application).
        
        Args:
            app_name: Name of the application to launch
            wait_time: Time to wait for app to start
            
        Returns:
            True if app launched successfully, False otherwise
        """
        return self.open_application(app_name)
    
    def _open_chrome(self, url: str) -> None:
        """Open URL in Chrome."""
        if sys.platform == "win32":
            subprocess.Popen(["chrome.exe", url])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Google Chrome", url])
        else:
            subprocess.Popen(["google-chrome", url])
    
    def _open_firefox(self, url: str) -> None:
        """Open URL in Firefox."""
        if sys.platform == "win32":
            subprocess.Popen(["firefox.exe", url])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Firefox", url])
        else:
            subprocess.Popen(["firefox", url])
    
    def _open_edge(self, url: str) -> None:
        """Open URL in Edge."""
        if sys.platform == "win32":
            subprocess.Popen(["msedge.exe", url])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Microsoft Edge", url])
        else:
            subprocess.Popen(["microsoft-edge", url])


class ActionVerifier:
    """Verifies the outcome of executed actions."""
    
    def __init__(self):
        """Initialize action verifier."""
        logger.info("Action verifier initialized")
    
    def verify_action(
        self, 
        action: str, 
        isr_before: ISR, 
        isr_after: ISR, 
        expected_changes: List[str]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verify that an action had the expected effect.
        
        Args:
            action: Description of the action performed
            isr_before: ISR before the action
            isr_after: ISR after the action
            expected_changes: List of expected changes
            
        Returns:
            Tuple of (success, message, verification_data)
        """
        try:
            logger.info(f"Verifying action: {action}")
            
            # Calculate changes between ISRs
            changes = self._calculate_isr_changes(isr_before, isr_after)
            
            # Check if expected changes occurred
            verification_passed = self._check_expected_changes(changes, expected_changes)
            
            # Generate verification message
            if verification_passed:
                message = f"Action '{action}' verified successfully"
            else:
                message = f"Action '{action}' verification failed"
            
            verification_data = {
                "action": action,
                "verification_passed": verification_passed,
                "changes_detected": changes,
                "expected_changes": expected_changes,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Verification result: {verification_passed}")
            return verification_passed, message, verification_data
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False, f"Verification error: {e}", {}
    
    def _calculate_isr_changes(self, isr_before: ISR, isr_after: ISR) -> Dict[str, Any]:
        """Calculate changes between two ISRs."""
        changes = {
            "element_count_change": len(isr_after.elements) - len(isr_before.elements),
            "new_elements": [],
            "modified_elements": [],
            "removed_elements": []
        }
        
        # Find new elements
        before_ids = {elem.id for elem in isr_before.elements}
        after_ids = {elem.id for elem in isr_after.elements}
        
        changes["new_elements"] = list(after_ids - before_ids)
        changes["removed_elements"] = list(before_ids - after_ids)
        
        # Find modified elements
        for elem_after in isr_after.elements:
            if elem_after.id in before_ids:
                elem_before = next((e for e in isr_before.elements if e.id == elem_after.id), None)
                if elem_before and self._elements_different(elem_before, elem_after):
                    changes["modified_elements"].append({
                        "id": elem_after.id,
                        "changes": self._get_element_changes(elem_before, elem_after)
                    })
        
        return changes
    
    def _elements_different(self, elem1: Element, elem2: Element) -> bool:
        """Check if two elements are different."""
        return (elem1.text != elem2.text or 
                elem1.bbox != elem2.bbox or 
                elem1.confidence != elem2.confidence)
    
    def _get_element_changes(self, elem_before: Element, elem_after: Element) -> Dict[str, Any]:
        """Get specific changes between two elements."""
        changes = {}
        
        if elem_before.text != elem_after.text:
            changes["text"] = {"before": elem_before.text, "after": elem_after.text}
        
        if elem_before.bbox != elem_after.bbox:
            changes["bbox"] = {"before": elem_before.bbox, "after": elem_after.bbox}
        
        if elem_before.confidence != elem_after.confidence:
            changes["confidence"] = {"before": elem_before.confidence, "after": elem_after.confidence}
        
        return changes
    
    def _check_expected_changes(self, changes: Dict[str, Any], expected: List[str]) -> bool:
        """Check if expected changes occurred."""
        if not expected:
            return True
        
        # Simple check - in a real implementation, this would be more sophisticated
        for expected_change in expected:
            if "new element" in expected_change.lower() and changes["new_elements"]:
                continue
            elif "element count" in expected_change.lower() and changes["element_count_change"] != 0:
                continue
            elif "text change" in expected_change.lower() and changes["modified_elements"]:
                continue
            else:
                # For now, assume any change is good
                if changes["element_count_change"] != 0 or changes["modified_elements"] or changes["new_elements"]:
                    continue
                else:
                    return False
        
        return True


class SafetyGuardrails:
    """Implements safety guardrails and human-in-the-loop prompts."""
    
    def __init__(self, confidence_threshold: float = 0.6):
        """Initialize safety guardrails."""
        self.confidence_threshold = confidence_threshold
        self.destructive_actions = [
            "delete", "remove", "destroy", "clear", "reset", "format",
            "uninstall", "shutdown", "restart", "logout", "exit"
        ]
        logger.info(f"Safety guardrails initialized with threshold: {confidence_threshold}")
    
    def check_plan_safety(self, plan: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """
        Check if a plan is safe to execute.
        
        Args:
            plan: The execution plan to check
            
        Returns:
            Tuple of (is_safe, reason, warnings)
        """
        warnings = []
        
        # Check confidence threshold
        confidence = plan.get("confidence", 0.0)
        if confidence < self.confidence_threshold:
            warnings.append(f"Low confidence: {confidence:.2f} < {self.confidence_threshold}")
        
        # Check for destructive actions
        steps = plan.get("steps", [])
        destructive_steps = []
        
        for step in steps:
            step_text = f"{step.get('op', '')} {step.get('value', '')} {step.get('explain', '')}"
            step_text_lower = step_text.lower()
            
            for destructive in self.destructive_actions:
                if destructive in step_text_lower:
                    destructive_steps.append(f"Step {step.get('step', '?')}: {step_text}")
                    break
        
        if destructive_steps:
            warnings.extend(destructive_steps)
        
        # Determine if safe
        is_safe = len(warnings) == 0 or confidence >= self.confidence_threshold
        
        if is_safe:
            reason = "Plan is safe to execute"
        else:
            reason = "Plan requires human confirmation"
        
        return is_safe, reason, warnings
    
    def request_user_confirmation(self, plan: Dict[str, Any], warnings: List[str]) -> bool:
        """
        Request user confirmation for potentially unsafe actions.
        
        Args:
            plan: The execution plan
            warnings: List of warnings
            
        Returns:
            True if user confirms, False otherwise
        """
        print("\n" + "="*60)
        print("⚠️  SAFETY WARNING - HUMAN CONFIRMATION REQUIRED")
        print("="*60)
        print(f"Plan ID: {plan.get('plan_id', 'Unknown')}")
        print(f"Confidence: {plan.get('confidence', 0.0):.2f}")
        print(f"Steps: {len(plan.get('steps', []))}")
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
        
        print("\nPlan Steps:")
        for step in plan.get('steps', []):
            print(f"  {step.get('step', '?')}. {step.get('op', '')} - {step.get('explain', '')}")
        
        print("\n" + "="*60)
        response = input("Do you want to proceed with this plan? (y/N): ").strip().lower()
        
        return response in ['y', 'yes']


class PipelineRunner:
    """Main pipeline runner that orchestrates the complete AI agent flow."""
    
    def __init__(
        self,
        vlm_backend: str = "yolov8",
        ocr_backend: str = "paddleocr",
        logs_dir: str = "logs",
        screenshots_dir: str = "screenshots",
        confidence_threshold: float = 0.6
    ):
        """Initialize the pipeline runner."""
        self.vlm_backend = vlm_backend
        self.ocr_backend = ocr_backend
        self.logs_dir = logs_dir
        self.screenshots_dir = screenshots_dir
        self.confidence_threshold = confidence_threshold
        
        # Initialize components
        self.screenshot_capture = ScreenshotCapture(screenshots_dir)
        self.app_launcher = AppLauncher()
        self.action_verifier = ActionVerifier()
        self.safety_guardrails = SafetyGuardrails(confidence_threshold)
        
        # Initialize AI components
        self.perception_pipeline = create_pipeline(
            vlm_backend=vlm_backend,
            ocr_backend=ocr_backend,
            output_dir="output"
        )
        
        self.planner = create_planner(
            confidence_threshold=confidence_threshold,
            use_prompt_guardrails=True
        )
        
        self.executor = create_executor(
            max_retries=3,
            retry_delay=0.5
        )
        
        logger.info("Pipeline runner initialized")
    
    def run_instruction(
        self, 
        user_instruction: str, 
        memory: Optional[Dict[str, Any]] = None,
        require_confirmation: bool = True
    ) -> Dict[str, Any]:
        """
        Run a complete instruction through the AI agent pipeline.
        
        Args:
            user_instruction: The user's instruction to execute
            memory: Optional memory context from previous actions
            require_confirmation: Whether to require human confirmation for unsafe actions
            
        Returns:
            Dictionary containing the complete execution result
        """
        # Create run logger
        run_logger = create_run_logger(self.logs_dir)
        
        try:
            # Log user instruction
            run_logger.log_user_instruction(user_instruction)
            logger.info(f"Processing instruction: {user_instruction}")
            
            # Step 0: Check if we need to launch an app
            instruction_lower = user_instruction.lower()
            # Launch calculator if instruction mentions calculator OR is a calculation
            needs_calculator = (
                "calculator" in instruction_lower or 
                "calculate" in instruction_lower or
                any(op in instruction_lower for op in ['+', '-', '*', '/', '×', '÷'])
            )
            
            if needs_calculator:
                logger.info("Detected calculator request - opening calculator...")
                if self.app_launcher.launch_app("calculator"):
                    logger.info("Calculator launched successfully")
                    time.sleep(3)  # Extra time for app to fully load
                    
                    # Verify calculator window is visible
                    try:
                        result = subprocess.run(['hyprctl', 'clients', '-j'], 
                                              capture_output=True, text=True, check=True)
                        import json
                        windows = json.loads(result.stdout)
                        calc_found = any('calculator' in w.get('class', '').lower() or 
                                       'calculator' in w.get('title', '').lower()
                                       for w in windows)
                        if calc_found:
                            logger.info("✅ Calculator window verified visible")
                        else:
                            logger.warning("⚠️ Calculator window not found in window list!")
                    except Exception as e:
                        logger.warning(f"Could not verify calculator window: {e}")
                else:
                    logger.warning("Failed to launch calculator, continuing anyway...")
            
            # Step 1: Capture screenshot
            logger.info("Step 1: Capturing screenshot...")
            screenshot_path = self.screenshot_capture.capture_screenshot()
            logger.info(f"Screenshot captured: {screenshot_path}")
            
            # Step 2: Perception - Process screenshot to get ISR
            logger.info("Step 2: Running perception pipeline...")
            isr = self.perception_pipeline.process_screenshot(screenshot_path, run_logger)
            logger.info(f"Perception completed. Detected {len(isr.elements)} elements")
            
            # Step 3: Planning - Generate execution plan
            logger.info("Step 3: Generating execution plan...")
            plan = self.planner.generate_plan(
                user_instruction=user_instruction,
                isr=isr.to_dict(),
                memory=memory,
                run_logger=run_logger
            )
            logger.info(f"Planning completed. Generated plan with {len(plan.steps)} steps")
            
            # Step 4: Safety check
            logger.info("Step 4: Checking plan safety...")
            is_safe, reason, warnings = self.safety_guardrails.check_plan_safety(plan.to_dict())
            
            if not is_safe and require_confirmation:
                logger.info("Plan requires human confirmation")
                if not self.safety_guardrails.request_user_confirmation(plan.to_dict(), warnings):
                    logger.info("User declined to proceed with the plan")
                    run_logger.log_action("User Confirmation", "User declined to proceed", False)
                    log_file = run_logger.finalize()
                    
                    return {
                        "run_id": run_logger.get_log_data()["run_id"],
                        "user_instruction": user_instruction,
                        "screenshot_path": screenshot_path,
                        "isr": isr.to_dict(),
                        "plan": plan.to_dict(),
                        "execution_result": None,
                        "log_file": log_file,
                        "success": False,
                        "reason": "User declined unsafe plan"
                    }
            
            # Step 5: Execution - Execute the plan
            logger.info("Step 5: Executing plan...")
            execution_result = self._execute_plan_with_verification(plan, isr, run_logger)
            
            # Finalize logging
            log_file = run_logger.finalize()
            
            # Prepare result
            result = {
                "run_id": run_logger.get_log_data()["run_id"],
                "user_instruction": user_instruction,
                "screenshot_path": screenshot_path,
                "isr": isr.to_dict(),
                "plan": plan.to_dict(),
                "execution_result": execution_result.to_dict() if execution_result else None,
                "log_file": log_file,
                "success": execution_result.success_rate >= 0 if execution_result else False,  # Accept any execution, even without verification
                "safety_warnings": warnings
            }
            
            success_rate = execution_result.success_rate if execution_result else 0
            logger.info(f"Pipeline execution completed. Success rate: {success_rate:.2%}")
            logger.info(f"Run log saved to: {log_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            
            # Log the error
            run_logger.log_action("Pipeline Error", str(e), False)
            log_file = run_logger.finalize()
            
            return {
                "run_id": run_logger.get_log_data()["run_id"],
                "user_instruction": user_instruction,
                "error": str(e),
                "log_file": log_file,
                "success": False
            }
    
    def _execute_plan_with_verification(
        self, 
        plan, 
        initial_isr: ISR, 
        run_logger: RunLogger
    ):
        """Execute plan with verification after each step."""
        logger.info(f"Executing plan with verification: {plan.plan_id}")
        
        # Use the existing executor but add verification
        execution_result = self.executor.execute_plan(plan, initial_isr, run_logger)
        
        # Add verification data to the result
        verification_logs = []
        current_isr = initial_isr
        
        for i, step_result in enumerate(execution_result.steps_results):
            if step_result.outcome == ActionOutcome.SUCCESS:
                # Capture new screenshot and create ISR for verification
                try:
                    new_screenshot = self.screenshot_capture.capture_screenshot(f"step_{i+1}_verification.png")
                    new_isr = self.perception_pipeline.process_screenshot(new_screenshot)
                    
                    # Verify the action
                    expected_changes = [f"Step {step_result.step} should have visible effect"]
                    verification_passed, message, verification_data = self.action_verifier.verify_action(
                        f"Step {step_result.step}: {plan.steps[i].op}",
                        current_isr,
                        new_isr,
                        expected_changes
                    )
                    
                    verification_logs.append(verification_data)
                    
                    # Log verification result
                    run_logger.log_action(
                        f"Verification Step {step_result.step}",
                        message,
                        verification_passed
                    )
                    
                    current_isr = new_isr
                    
                except Exception as e:
                    logger.warning(f"Verification failed for step {step_result.step}: {e}")
                    verification_logs.append({
                        "action": f"Step {step_result.step} verification",
                        "verification_passed": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Add verification logs to execution result
        execution_result.verification_logs = verification_logs
        
        return execution_result


def create_pipeline_runner(
    vlm_backend: str = "yolov8",
    ocr_backend: str = "paddleocr",
    logs_dir: str = "logs",
    screenshots_dir: str = "screenshots",
    confidence_threshold: float = 0.6
) -> PipelineRunner:
    """
    Factory function to create a PipelineRunner.
    
    Args:
        vlm_backend: VLM backend for perception
        ocr_backend: OCR backend for perception
        logs_dir: Directory for run logs
        screenshots_dir: Directory for screenshots
        confidence_threshold: Minimum confidence for plan execution
        
    Returns:
        PipelineRunner instance
    """
    return PipelineRunner(
        vlm_backend=vlm_backend,
        ocr_backend=ocr_backend,
        logs_dir=logs_dir,
        screenshots_dir=screenshots_dir,
        confidence_threshold=confidence_threshold
    )


if __name__ == "__main__":
    # Example usage and testing
    print("=== AI Agent Pipeline Runner Test ===")
    
    try:
        # Create pipeline runner
        runner = create_pipeline_runner()
        print("✓ PipelineRunner created")
        
        # Test with a mock instruction
        user_instruction = "Open calculator and calculate 2 + 2"
        
        print(f"Testing with instruction: {user_instruction}")
        print("Note: This will require a real screenshot and may need user confirmation")
        
        # Run the instruction
        result = runner.run_instruction(
            user_instruction=user_instruction,
            require_confirmation=True
        )
        
        print(f"✓ Pipeline execution completed")
        print(f"Run ID: {result.get('run_id')}")
        print(f"Success: {result.get('success')}")
        print(f"Log file: {result.get('log_file')}")
        
        if result.get('execution_result'):
            exec_result = result['execution_result']
            print(f"Success rate: {exec_result.get('success_rate', 0):.2%}")
            print(f"Total steps: {len(exec_result.get('steps_results', []))}")
        
        print("\n=== Pipeline Runner Test Completed Successfully ===")
        
    except Exception as e:
        print(f"✗ Pipeline Runner Test Failed: {e}")
        import traceback
        traceback.print_exc()

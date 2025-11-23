# Fix Screenshot Issues on Wayland/Hyprland and Add Windows Support

## Goal Description
The current screenshot implementation in `pipeline_runner.py` fails on Arch Linux with Wayland/Hyprland because it relies on a brittle, hardcoded method that attempts to find and capture only a "calculator" window. It also lacks proper dependency definitions for Windows support (`mss`, `pyautogui`).

This plan aims to:
1.  Make the screenshot logic on Wayland robust by using standard tools (`grim`) to capture the full screen by default, removing the flaky window-specific logic.
2.  Ensure Windows compatibility by adding necessary dependencies and verifying the Windows capture path.
3.  Clean up the `ScreenshotCapture` class to be more general-purpose.

## User Review Required
> [!IMPORTANT]
> I am removing the logic that specifically tries to capture *only* the calculator window on Hyprland. The agent will now capture the full screen on Wayland, similar to how it works on other platforms. This is more reliable but means the agent sees the whole desktop.

## Proposed Changes

### Dependencies
#### [MODIFY] [requirements.txt](file:///home/krishang/Work/Icarus-DevJams/ai-agents/mainmlfile/perception/requirements.txt)
- Add `mss>=9.0.0` (for fast Windows screenshots)
- Add `pyautogui>=0.9.50` (for cross-platform control and fallback screenshots)

### Perception Pipeline
#### [MODIFY] [pipeline_runner.py](file:///home/krishang/Work/Icarus-DevJams/ai-agents/mainmlfile/perception/pipeline_runner.py)
- **Remove** `_capture_hyprland_calculator` method.
- **Update** `_capture_linux`:
    -   Prioritize `grim` for full-screen capture on Wayland.
    -   Remove the call to the calculator-specific capture.
    -   Retain X11 fallbacks (`scrot`, `gnome-screenshot`, etc.).
-   **Verify** `_capture_windows` uses `mss` correctly.

## Verification Plan

### Automated Tests
-   Run `python3 -c "import mss; import pyautogui; print('Dependencies installed')"` to verify imports.

### Manual Verification
-   I will provide a script `test_screenshot_capability.py` that the user can run.
-   **User Action**: Run `python3 test_screenshot_capability.py`
    -   This script will attempt to take a screenshot using the refactored logic and save it to `test_screenshot.png`.
    -   If successful, it confirms the fix works on the user's specific environment (Wayland/Hyprland).

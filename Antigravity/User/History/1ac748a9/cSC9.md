# Task: Fix Screenshot Issues and Add Windows Compatibility

- [x] Analyze `pipeline_runner.py` to understand current screenshot implementation <!-- id: 0 -->
- [x] Update `requirements.txt` with `mss` and `pyautogui` <!-- id: 4 -->
- [x] Refactor `pipeline_runner.py` for robust screenshot capture <!-- id: 5 -->
    - [x] Remove `_capture_hyprland_calculator`
    - [x] Implement strict `grim` for Wayland
    - [x] Implement strict `mss` for Windows
- [x] Verify changes with test script <!-- id: 3 -->
- [x] Verify full flow: "calculator 20+20" with mouse clicks <!-- id: 6 -->
- [x] Fix UIElement schema mismatch (embedding attribute) <!-- id: 7 -->

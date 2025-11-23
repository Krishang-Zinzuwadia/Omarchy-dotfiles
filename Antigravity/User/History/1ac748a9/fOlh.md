# Task: Fix Screenshot Issues and Add Windows Compatibility

- [x] Analyze `pipeline_runner.py` to understand current screenshot implementation <!-- id: 0 -->
- [ ] Update `requirements.txt` with `mss` and `pyautogui` <!-- id: 4 -->
- [ ] Refactor `pipeline_runner.py` for robust screenshot capture <!-- id: 5 -->
    - [ ] Remove `_capture_hyprland_calculator`
    - [ ] Implement strict `grim` for Wayland
    - [ ] Implement strict `mss` for Windows
- [ ] Verify changes with test script <!-- id: 3 -->

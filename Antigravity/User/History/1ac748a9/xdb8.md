# Task: Fix Screenshot Issues and Add Windows Compatibility

- [ ] Analyze `pipeline_runner.py` to understand current screenshot implementation <!-- id: 0 -->
- [ ] Research and implement Wayland/Hyprland screenshot support <!-- id: 1 -->
    - [ ] Check for `grim` and `slurp` or `hyprctl` usage
    - [ ] Implement fallback or specific handler for Wayland
- [ ] Research and implement Windows screenshot support <!-- id: 2 -->
    - [ ] Ensure `PIL` or `pyautogui` is used correctly for Windows
- [ ] Verify changes <!-- id: 3 -->

# Common AI Agent Pipeline Errors

## Planning Failures

### "Plan confidence below threshold"
**Error Log:** `WARNING:prompt_guardrails:Plan confidence X.XX below threshold Y.YY`
**Context:** The Planner generated a plan, but the Safety Guardrails or the Planner's own self-evaluation deemed it risky or incorrect.

**Possible Causes:**
1.  **VLM Blindness:** The VLM (Vision Language Model) cannot clearly see the UI elements in the screenshot (e.g., low resolution, clutter, or the element is hidden).
2.  **Ambiguous Instruction:** The user prompt is too vague for the model to form a confident plan.
3.  **Strict Guardrails:** The confidence threshold (e.g., 0.6) might be too high for the current model's capabilities.
4.  **Prompt Engineering:** The system prompt might not be guiding the model correctly to output high-confidence actions.

**Troubleshooting:**
-   Check the `screenshots/` directory to see exactly what the agent saw at the time of failure.
-   Lower the confidence threshold temporarily to see if the plan is actually valid.
-   Simplify the user instruction.

## Perception Failures

### "Screenshot capture failed" / "File missing or empty"
**Context:** The agent cannot generate the initial visual input.

**Possible Causes:**
-   **Wayland/Hyprland:** Using X11 tools (`scrot`, `xwd`) instead of Wayland native tools (`grim`).
-   **Windows:** Missing `mss` dependency.
-   **Permissions:** OS blocking screen recording.

**Troubleshooting:**
-   See `cross_platform_screenshot_implementation` KI for platform-specific fixes.

## Code/Schema Failures

### "AttributeError: 'UIElement' object has no attribute 'embedding'"
**Error Log:** `Pipeline execution failed: 'UIElement' object has no attribute 'embedding'`
**Context:** The pipeline crashed during the perception or planning phase, likely when processing the Intermediate State Representation (ISR).

**Possible Causes:**
1.  **Schema Mismatch:** The `UIElement` class definition differs between modules (e.g., `vlm_detector.py` has an `embedding` field while `ui_detector.py` does not). This often happens when multiple detectors define their own `UIElement` dataclass instead of importing a shared one.
2.  **Version Incompatibility:** The VLM backend might be returning data that the current schema doesn't support, or vice versa.

**Troubleshooting:**
-   **Unify Definitions:** Ensure all modules import `UIElement` from a single source of truth (e.g., `isr_schema.py`) or have identical dataclass definitions.
-   **Check Attributes:** Verify that all required attributes (like `embedding`) are present in all `UIElement` instantiations across different detectors.
-   **Inspect the VLM backend's output format.**

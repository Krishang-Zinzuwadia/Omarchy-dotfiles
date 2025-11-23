# AI Agent Pipeline Testing Strategy

Reliable AI agents require a layered testing approach to isolate failures in the Perception-Planning-Execution loop.

## Component-Level Verification

Before running full end-to-end tasks, verify individual capabilities with dedicated scripts. This isolates infrastructure issues (e.g., missing dependencies, OS incompatibilities) from AI logic issues (e.g., VLM hallucinations).

### 1. Perception Layer (Screenshots)
**Goal:** Ensure the agent can "see" the screen.
**Common Failure:** Black screens, permission errors, wrong window focus.
**Verification Pattern:**
- Create a script (e.g., `verify_screenshot.py`) that only captures and saves a screenshot.
- Check file existence and size.
- **Do not** involve the VLM or Planner in this step.

### 2. Action Layer (Mouse/Keyboard)
**Goal:** Ensure the agent can "act".
**Common Failure:** Wayland security restrictions, missing accessibility permissions.
**Verification Pattern:**
- Create a script that performs a simple, harmless action (e.g., move mouse in a square, type into a text editor).

## End-to-End Flow Verification

Once components are verified, run a "Full Flow" test.

### Full Flow Test
**Goal:** Verify the integration of Perception -> VLM -> Planner -> Executor.
**Pattern:**
- Use a deterministic, simple prompt (e.g., "Open calculator and type 20+20").
- **Failure Analysis:**
    - If it fails here but component tests passed, the issue is likely in the **AI Logic** (VLM interpretation or Planner prompt adherence).
    - Check logs for "Confidence Score" or "Guardrail" rejections.

## Debugging Flow Example

1. **Symptom:** Agent fails to click a button.
2. **Step 1:** Run `verify_screenshot.py`.
    - *Result:* Black image.
    - *Diagnosis:* Fix screenshot tool (e.g., switch to `grim` on Wayland).
3. **Step 2:** Run `verify_screenshot.py` again.
    - *Result:* Clear image.
4. **Step 3:** Run Full Flow.
    - *Result:* "Plan confidence too low".
    - *Diagnosis:* VLM didn't recognize the button in the screenshot. Adjust prompt or VLM model.

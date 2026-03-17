"""
Computer use demo with a proper agentic loop.

Requirements:
    pip install anthropic pyautogui pillow

Usage:
    python computer_use_demo.py
"""

import anthropic
import base64
import subprocess
import io
from typing import Any

try:
    import pyautogui
    from PIL import ImageGrab
    DESKTOP_AVAILABLE = True
except ImportError:
    DESKTOP_AVAILABLE = False
    print("Warning: pyautogui/pillow not installed. Install with: pip install pyautogui pillow")


def take_screenshot() -> str:
    """Capture the screen and return as base64-encoded PNG."""
    screenshot = ImageGrab.grab()
    buf = io.BytesIO()
    screenshot.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def execute_computer_action(action: str, **kwargs: Any) -> dict[str, Any]:
    """Execute a computer action and return a screenshot result."""
    if action == "screenshot":
        pass  # Just take a screenshot below
    elif action == "left_click":
        pyautogui.click(kwargs["coordinate"][0], kwargs["coordinate"][1])
    elif action == "double_click":
        pyautogui.doubleClick(kwargs["coordinate"][0], kwargs["coordinate"][1])
    elif action == "right_click":
        pyautogui.rightClick(kwargs["coordinate"][0], kwargs["coordinate"][1])
    elif action == "middle_click":
        pyautogui.middleClick(kwargs["coordinate"][0], kwargs["coordinate"][1])
    elif action == "type":
        pyautogui.typewrite(kwargs["text"], interval=0.05)
    elif action == "key":
        pyautogui.hotkey(*kwargs["text"].split("+"))
    elif action == "mouse_move":
        pyautogui.moveTo(kwargs["coordinate"][0], kwargs["coordinate"][1])
    elif action == "left_click_drag":
        start = kwargs["start_coordinate"]
        end = kwargs["coordinate"]
        pyautogui.drag(end[0] - start[0], end[1] - start[1], button="left")
    elif action == "scroll":
        direction = kwargs.get("direction", "down")
        amount = kwargs.get("amount", 3)
        x, y = kwargs["coordinate"]
        pyautogui.moveTo(x, y)
        pyautogui.scroll(amount if direction == "up" else -amount)
    elif action == "cursor_position":
        x, y = pyautogui.position()
        return {"type": "text", "text": f"Cursor position: ({x}, {y})"}

    # After every action, return a fresh screenshot
    screenshot_b64 = take_screenshot()
    return {
        "type": "tool_result",
        "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}}],
    }


def execute_bash(command: str) -> str:
    """Run a bash command and return its output."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout
    if result.returncode != 0:
        output += f"\nstderr: {result.stderr}"
    return output or "(no output)"


def execute_text_editor(command: str, **kwargs: Any) -> str:
    """Execute a str_replace_based_edit_tool command."""
    path = kwargs.get("path", "")
    if command == "view":
        try:
            with open(path) as f:
                return f.read()
        except FileNotFoundError:
            return f"File not found: {path}"
    elif command == "create":
        with open(path, "w") as f:
            f.write(kwargs.get("file_text", ""))
        return f"Created {path}"
    elif command == "str_replace":
        with open(path) as f:
            content = f.read()
        old = kwargs["old_str"]
        new = kwargs["new_str"]
        if old not in content:
            return f"Error: old_str not found in {path}"
        with open(path, "w") as f:
            f.write(content.replace(old, new, 1))
        return f"Replaced in {path}"
    elif command == "insert":
        with open(path) as f:
            lines = f.readlines()
        line_num = kwargs.get("insert_line", 0)
        lines.insert(line_num, kwargs.get("new_str", "") + "\n")
        with open(path, "w") as f:
            f.writelines(lines)
        return f"Inserted at line {line_num} in {path}"
    return f"Unknown command: {command}"


def run_computer_use_agent(task: str, max_iterations: int = 20) -> None:
    """Run the computer use agentic loop."""
    if not DESKTOP_AVAILABLE:
        raise RuntimeError("pyautogui and pillow are required. Run: pip install pyautogui pillow")

    client = anthropic.Anthropic()

    # Start with a screenshot so Claude knows the current state
    initial_screenshot = take_screenshot()
    messages: list[dict] = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/png", "data": initial_screenshot},
                },
                {"type": "text", "text": task},
            ],
        }
    ]

    tools = [
        {
            "type": "computer_20251124",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
            "display_number": 1,
        },
        {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
        {"type": "bash_20250124", "name": "bash"},
    ]

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = client.beta.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages,
            betas=["computer-use-2025-11-24"],
        )

        print(f"Stop reason: {response.stop_reason}")

        # Print any text Claude says
        for block in response.content:
            if block.type == "text":
                print(f"Claude: {block.text}")

        # Done — no more tool calls
        if response.stop_reason == "end_turn":
            print("\nTask complete.")
            break

        if response.stop_reason != "tool_use":
            print(f"Unexpected stop reason: {response.stop_reason}")
            break

        # Append Claude's response to history
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool call and collect results
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"Tool: {block.name} | Input: {block.input}")
            tool_result_content: Any = None

            if block.name == "computer":
                action = block.input.get("action", "screenshot")
                result = execute_computer_action(action, **{k: v for k, v in block.input.items() if k != "action"})
                tool_result_content = result.get("content", result)
            elif block.name == "bash":
                output = execute_bash(block.input.get("command", ""))
                tool_result_content = output
            elif block.name == "str_replace_based_edit_tool":
                command = block.input.get("command", "")
                output = execute_text_editor(command, **{k: v for k, v in block.input.items() if k != "command"})
                tool_result_content = output

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": tool_result_content,
            })

        # Send all tool results back as a user message
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\nReached max iterations ({max_iterations}).")


if __name__ == "__main__":
    run_computer_use_agent("Save a picture of a cat to my desktop.")

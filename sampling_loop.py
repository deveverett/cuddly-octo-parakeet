"""
Agentic sampling loop for Claude computer use.

Handles the back-and-forth between:
1. Sending user messages to Claude
2. Claude requesting tool use
3. Your app executing those tools
4. Sending tool results back to Claude
"""

from anthropic import Anthropic

# Maps tool_version → the correct `name` the API requires for that version.
# The text editor name changed in 20250429; computer and bash are stable.
_TEXT_EDITOR_NAMES: dict[str, str] = {
    "20250728": "str_replace_based_edit_tool",
    "20250429": "str_replace_based_edit_tool",
    "20250124": "str_replace_editor",
    "20241022": "str_replace_editor",
}

_BETA_FLAGS: dict[str, str] = {
    "20251124": "computer-use-2025-11-24",
    "20250124": "computer-use-2025-01-24",
    "20241022": "computer-use-2024-10-22",
}


def sampling_loop(
    *,
    model: str,
    messages: list[dict],
    api_key: str,
    max_tokens: int = 4096,
    tool_version: str,
    thinking_budget: int | None = None,
    max_iterations: int = 10,
) -> list[dict]:
    """
    Run the computer-use agentic loop until Claude stops calling tools
    or max_iterations is reached.

    Args:
        model: Claude model ID (e.g. "claude-opus-4-6").
        messages: Conversation history (mutated in-place and returned).
        api_key: Anthropic API key.
        max_tokens: Max output tokens per API call.
        tool_version: Date suffix used by all three tool types, e.g. "20251124".
        thinking_budget: Enables extended thinking.
            Pass a token budget for legacy models that require it.
            On Opus/Sonnet 4.x, adaptive thinking is used instead (budget ignored).
            Pass None to disable thinking entirely.
        max_iterations: Safety cap to prevent runaway API spend.

    Returns:
        The updated messages list.
    """
    client = Anthropic(api_key=api_key)

    # Resolve the beta header and tool names for this tool_version.
    beta_flag = _BETA_FLAGS.get(tool_version, "computer-use-2024-10-22")
    editor_name = _TEXT_EDITOR_NAMES.get(tool_version, "str_replace_editor")

    tools = [
        {
            "type": f"computer_{tool_version}",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
        },
        {"type": f"text_editor_{tool_version}", "name": editor_name},
        {"type": f"bash_{tool_version}", "name": "bash"},
    ]

    # Build thinking config if requested.
    # Opus/Sonnet 4.x use adaptive thinking; older models need an explicit budget.
    thinking: dict | None = None
    if thinking_budget is not None:
        if "opus-4" in model or "sonnet-4" in model:
            thinking = {"type": "adaptive"}
        else:
            thinking = {"type": "enabled", "budget_tokens": thinking_budget}

    for _ in range(max_iterations):
        # Only include `thinking` when it's actually set — passing None raises an error.
        extra = {"thinking": thinking} if thinking is not None else {}

        response = client.beta.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools,
            betas=[beta_flag],
            **extra,
        )

        # Append Claude's response to history before processing tool calls.
        messages.append({"role": "assistant", "content": response.content})

        # Use stop_reason — more reliable than checking whether tool_results is empty.
        if response.stop_reason != "tool_use":
            return messages

        # Execute each tool call and collect results.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            # Replace this with real tool dispatch in your application.
            result: str = f"Executed {block.name} successfully"

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    # content must be a string or list[ContentBlock], not a dict.
                    "content": result,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return messages

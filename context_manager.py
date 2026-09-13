from pathlib import Path

from config import (
    WORKSPACE_DIR,
    KEEP_RECENT_MESSAGES,
    SUMMARIZE_AFTER_MESSAGES,
    MAX_SUMMARY_CHARS,
)


SUMMARY_FILE = (
    WORKSPACE_DIR / "CONTEXT_SUMMARY.md"
)


def read_summary() -> str:
    if not SUMMARY_FILE.exists():
        return ""

    return SUMMARY_FILE.read_text(
        encoding="utf-8"
    )


def write_summary(summary: str) -> None:
    SUMMARY_FILE.write_text(
        summary[:MAX_SUMMARY_CHARS],
        encoding="utf-8"
    )

def normalize_message(message) -> dict:

    if isinstance(message, dict):
        return message

    result = {
        "role": message.role
    }

    if message.content is not None:
        result["content"] = message.content
    else:
        result["content"] = None

    if getattr(message, "tool_calls", None):

        result["tool_calls"] = []

        for tool_call in message.tool_calls:

            result["tool_calls"].append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": (
                            tool_call.function.name
                        ),
                        "arguments": (
                            tool_call.function.arguments
                        ),
                    },
                }
            )

    return result

def should_compress(
    messages: list[dict]
) -> bool:

    non_system_messages = [
        msg
        for msg in messages
        if msg.get("role") != "system"
    ]

    return (
        len(non_system_messages)
        >= SUMMARIZE_AFTER_MESSAGES
    )

def find_safe_cut_index(
    messages: list[dict]
) -> int:

    if len(messages) <= KEEP_RECENT_MESSAGES:
        return 0

    cut_index = (
        len(messages)
        - KEEP_RECENT_MESSAGES
    )

    while (
        cut_index > 1
        and messages[cut_index].get("role")
        == "tool"
    ):
        cut_index -= 1

    return cut_index

def messages_to_text(
    messages: list[dict]
) -> str:

    parts = []

    for msg in messages:

        role = msg.get(
            "role",
            "unknown"
        )

        content = msg.get("content")

        if content:
            parts.append(
                f"{role.upper()}:\n{content}"
            )

        tool_calls = msg.get(
            "tool_calls",
            []
        )

        for tool_call in tool_calls:

            function = tool_call.get(
                "function",
                {}
            )

            parts.append(
                "ASSISTANT TOOL CALL:\n"
                f"Tool: {function.get('name')}\n"
                f"Arguments: "
                f"{function.get('arguments')}"
            )

    return "\n\n".join(parts)


def summarize_old_context(
    client,
    model: str,
    old_messages: list[dict],
    previous_summary: str,
) -> str:

    old_text = messages_to_text(
        old_messages
    )

    prompt = f"""
Summarize the earlier conversation context concisely and accurately.

The summary will provide useful context for future tasks.

PRESERVE:

- the user's goals;
- important decisions;
- created or modified files;
- project structure;
- important technical details;
- previous errors and their resolutions;
- unfinished tasks;
- important user preferences;
- relevant tool results.

DO NOT PRESERVE:

- casual conversation;
- repetition;
- lengthy raw tool output;
- irrelevant debugging details.

Write a concise, structured Markdown summary.

PREVIOUS SUMMARY:

{previous_summary}

CONVERSATION TO SUMMARIZE:

{old_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You create precise, concise "
                    "conversation context summaries."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        reasoning_effort="low",
    )

    summary = (
        response
        .choices[0]
        .message
        .content
    )

    return summary

def compress_context(
    client,
    model: str,
    messages: list[dict],
) -> list[dict]:

    if not should_compress(messages):
        return messages

    cut_index = find_safe_cut_index(
        messages
    )

    if cut_index <= 1:
        return messages

    system_message = messages[0]

    old_messages = messages[
        1:cut_index
    ]

    recent_messages = messages[
        cut_index:
    ]

    previous_summary = read_summary()

    new_summary = summarize_old_context(
        client=client,
        model=model,
        old_messages=old_messages,
        previous_summary=previous_summary,
    )

    write_summary(
        new_summary
    )

    summary_message = {
        "role": "system",
        "content": f"""
The following summary is derived from earlier conversations.

Use it as background information, but always give priority to newer messages.

--- CONTEXT SUMMARY ---

{new_summary}

--- END CONTEXT SUMMARY ---
""",
    }

    return [
        system_message,
        summary_message,
        *recent_messages,
    ]

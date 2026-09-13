import json

from groq import Groq

from config import (
    GROQ_API_KEY,
    MODEL,
    MAX_AGENT_STEPS,
    MAX_TOOL_OUTPUT,
)

from prompts import SYSTEM_PROMPT

from tools import (
    TOOL_SCHEMAS,
    execute_tool,
)

from context_manager import (
    compress_context,
    normalize_message,
)

client = Groq(
    api_key=GROQ_API_KEY
)


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def limit_tool_output(result: str) -> str:
    """Keep individual tool results within the configured context budget."""
    if len(result) <= MAX_TOOL_OUTPUT:
        return result

    return (
        result[:MAX_TOOL_OUTPUT]
        + "\n\n[Tool output truncated to preserve the context budget.]"
    )


def run_agent(user_message: str) -> str:
    global messages

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    messages = compress_context(
        client=client,
        model=MODEL,
        messages=messages,
    )

    for step in range(
        MAX_AGENT_STEPS
    ):

        response = (
            client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                reasoning_effort="medium",
            )
        )

        message = (
            response
            .choices[0]
            .message
        )

        normalized = normalize_message(
            message
        )

        messages.append(
            normalized
        )

        tool_calls = (
            message.tool_calls
        )

        if not tool_calls:
            return (
                message.content
                or ""
            )

        for tool_call in tool_calls:

            tool_name = (
                tool_call
                .function
                .name
            )

            try:

                arguments = json.loads(
                    tool_call
                    .function
                    .arguments
                )

                print(
                    f"\n[TOOL] "
                    f"{tool_name}"
                )

                print(
                    f"[ARGS] "
                    f"{arguments}"
                )

                result = (
                    execute_tool(
                        tool_name,
                        arguments
                    )
                )

                result = limit_tool_output(result)

            except Exception as e:

                result = (
                    f"Tool execution error: {e}"
                )

            print(
                f"[RESULT]\n"
                f"{result[:1000]}"
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": (
                        tool_call.id
                    ),
                    "name": tool_name,
                    "content": result,
                }
            )

        messages = compress_context(
            client=client,
            model=MODEL,
            messages=messages,
        )

    return (
        "The maximum number of agent steps "
        "has been reached."
    )

def main():

    print()
    print("=" * 60)
    print("MY HERMES — GROQ AGENT")
    print("=" * 60)

    print(
        "\nType 'exit' to quit.\n"
    )

    while True:

        user_input = input(
            "\nYou > "
        ).strip()

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit",
            "/exit"
        }:
            break

        try:

            answer = run_agent(
                user_input
            )

            print(
                f"\nHermes > {answer}"
            )

        except Exception as e:

            print(
                f"\n[ERROR] {e}"
            )


if __name__ == "__main__":
    main()

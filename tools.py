from pathlib import Path

from config import WORKSPACE_DIR

def execute_tool(
    tool_name: str,
    arguments: dict
) -> str:

    if tool_name == "list_files":
        return list_files(**arguments)

    if tool_name == "read_file":
        return read_file(**arguments)

    if tool_name == "write_file":
        return write_file(**arguments)

    if tool_name == "edit_file":
        return edit_file(**arguments)

    return f"Unknown tool: {tool_name}"


def safe_path(relative_path: str) -> Path:
    path = (WORKSPACE_DIR / relative_path).resolve()

    if path != WORKSPACE_DIR and WORKSPACE_DIR not in path.parents:
        raise ValueError(
            "The requested path is outside the workspace directory."
        )

    return path

#-----------------------------------------------------------------------------

def list_files(path: str = ".") -> str:
    try:
        directory = safe_path(path)

        if not directory.exists():
            return f"Directory does not exist: {path}"

        if not directory.is_dir():
            return f"Not a directory: {path}"

        results = []

        for item in sorted(directory.iterdir()):
            relative = item.relative_to(WORKSPACE_DIR)

            if item.is_dir():
                results.append(f"[DIR]  {relative}")
            else:
                results.append(f"[FILE] {relative}")

        if not results:
            return "The directory is empty."

        return "\n".join(results)

    except Exception as e:
        return f"Error: {e}"

#-----------------------------------------------------Olvas------------------------


def read_file(path: str) -> str:
    try:
        file_path = safe_path(path)

        if not file_path.exists():
            return f"File does not exist: {path}"

        if not file_path.is_file():
            return f"Not a file: {path}"

        return file_path.read_text(
            encoding="utf-8"
        )

    except Exception as e:
        return f"Error: {e}"

#-----------------------------------------------------Ir------------------------

def write_file(path: str, content: str) -> str:
    try:
        file_path = safe_path(path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return f"Successfully wrote: {path}"

    except Exception as e:
        return f"Error: {e}"

#-----------------------------------------------------Modosit------------------------

def edit_file(
    path: str,
    old_text: str,
    new_text: str
) -> str:

    try:
        file_path = safe_path(path)

        if not file_path.exists():
            return f"File does not exist: {path}"

        content = file_path.read_text(
            encoding="utf-8"
        )

        if old_text not in content:
            return (
                "The requested text was not found "
                "in the file."
            )

        occurrences = content.count(old_text)

        if occurrences > 1:
            return (
                f"The requested text occurs {occurrences} times. "
                "Provide a more specific excerpt."
            )

        new_content = content.replace(
            old_text,
            new_text,
            1
        )

        file_path.write_text(
            new_content,
            encoding="utf-8"
        )

        return f"Successfully updated: {path}"

    except Exception as e:
        return f"Error: {e}"


def read_memory() -> str:
    return read_file(
        "MEMORY.md"
    )


def write_memory(
    content: str
) -> str:

    return write_file(
        "MEMORY.md",
        content
    )

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "Lists files and subdirectories in a workspace directory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Relative directory path. "
                            "Default: ."
                        )
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Reads the complete contents of a text file in the workspace."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    }
                },
                "required": ["path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Creates or completely overwrites a file in the workspace."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": [
                    "path",
                    "content"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Replaces an exact text fragment in an existing file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "old_text": {
                        "type": "string"
                    },
                    "new_text": {
                        "type": "string"
                    }
                },
                "required": [
                    "path",
                    "old_text",
                    "new_text"
                ]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "read_memory",
        "description": (
            "Reads the assistant's persistent memory."
        ),
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "write_memory",
        "description": (
            "Updates the assistant's persistent memory. "
            "Only long-term useful information may be stored."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string"
                }
            },
            "required": [
                "content"
            ]
        }
    }
}
]

# My Hermes

My Hermes is a compact command-line assistant that can inspect, create, and update text files inside a dedicated workspace. It uses Groq for model access and keeps a short rolling summary so longer sessions remain manageable.

## Requirements

- Python 3.10 or later
- A Groq API key

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the packages:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then add your API key:

```env
GROQ_API_KEY=your_key_here
```

## Run

```bash
python agent.py
```

Enter a request at the prompt. Type `exit`, `quit`, or `/exit` to close the program.

## Shell sandbox

Shell commands are executed in a Docker container rather than on the host system. The container has no network access, runs as a non-root user, has a read-only base filesystem, and can write only to `workspace/`.

Start Docker Desktop, then build the sandbox image once:

```bash
docker build -t my-hermes-sandbox:latest .
```

After the image is available, Hermes can use its `execute_shell` tool for non-interactive commands such as running a script or checking a generated file. Commands are limited to 30 seconds by default and cannot access host files outside the workspace.

Set `SANDBOX_IMAGE` in `.env` only if you build the image with a different tag.

## Project layout

| Path | Purpose |
| --- | --- |
| `agent.py` | Command-line entry point and tool-call loop. |
| `prompts.py` | Core behaviour and operating guidelines. |
| `tools.py` | Workspace-only file operations exposed to the assistant. |
| `sandbox.py` | Docker-backed command execution with isolation and resource limits. |
| `Dockerfile` | Definition of the restricted shell environment. |
| `context_manager.py` | Conversation summarisation for longer sessions. |
| `skills/` | Optional task-specific instructions. |
| `workspace/` | Files available for the assistant to work with. |

## Notes

- The assistant can only access files inside `workspace/`.
- `.env`, persistent memory, and conversation summaries are excluded from version control.
- Change `MODEL` in `config.py` if you want to use another Groq-compatible model.

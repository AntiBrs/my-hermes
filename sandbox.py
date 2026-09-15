"""Run commands in a short-lived Docker sandbox."""

from __future__ import annotations

import shutil
import subprocess
from uuid import uuid4

from config import (
    SANDBOX_IMAGE,
    SANDBOX_MAX_TIMEOUT_SECONDS,
    SANDBOX_TIMEOUT_SECONDS,
    WORKSPACE_DIR,
)


def _validated_timeout(timeout_seconds: int | None) -> int:
    if timeout_seconds is None:
        return SANDBOX_TIMEOUT_SECONDS

    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int):
        raise ValueError("timeout_seconds must be an integer.")

    if not 1 <= timeout_seconds <= SANDBOX_MAX_TIMEOUT_SECONDS:
        raise ValueError(
            "timeout_seconds must be between 1 and "
            f"{SANDBOX_MAX_TIMEOUT_SECONDS}."
        )

    return timeout_seconds


def run_in_sandbox(
    command: str,
    timeout_seconds: int | None = None,
) -> str:
    """Run a non-interactive command with access limited to the workspace."""
    if not isinstance(command, str) or not command.strip():
        return "Error: command must be a non-empty string."

    try:
        timeout = _validated_timeout(timeout_seconds)
    except ValueError as error:
        return f"Error: {error}"

    docker = shutil.which("docker")
    if docker is None:
        return "Error: Docker is not installed or is not available on PATH."

    container_name = f"my-hermes-sandbox-{uuid4().hex}"

    docker_command = [
        docker,
        "run",
        "--rm",
        "--name",
        container_name,
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "64",
        "--memory",
        "512m",
        "--cpus",
        "1.0",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=64m",
        "--mount",
        f"type=bind,source={WORKSPACE_DIR},target=/workspace",
        "--workdir",
        "/workspace",
        SANDBOX_IMAGE,
        "timeout",
        "--signal=KILL",
        f"{timeout}s",
        "/bin/sh",
        "-lc",
        command,
    ]

    try:
        completed = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout + 5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(
                [docker, "rm", "--force", container_name],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        return f"Error: command exceeded the {timeout}-second time limit."
    except OSError as error:
        return f"Error: unable to start Docker: {error}"

    output = "\n".join(
        value.strip()
        for value in (completed.stdout, completed.stderr)
        if value.strip()
    )

    if completed.returncode == 0:
        return output or "Command completed successfully."

    if completed.returncode in {124, 137}:
        return f"Error: command exceeded the {timeout}-second time limit."

    docker_engine_errors = (
        "Cannot connect to the Docker daemon",
        "error during connect",
        "docker_engine",
    )
    if any(error in output for error in docker_engine_errors):
        return "Error: Docker is installed, but its engine is not running."

    if "Unable to find image" in output:
        return (
            f"Error: sandbox image '{SANDBOX_IMAGE}' is not available. "
            "Start Docker and run: docker build -t "
            f"{SANDBOX_IMAGE} ."
        )

    return f"Command exited with code {completed.returncode}.\n{output}"

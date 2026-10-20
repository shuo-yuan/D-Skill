# Modified from Trace2Skill (https://github.com/Qwen-Applications/Trace2Skill, Apache-2.0) for D-Skill; see NOTICE.
"""
Bash command execution tool.
"""

import re
import subprocess
import sys
import os

# Add parent src to path for react_agent imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "third_party", "trace2skill", "src"))

from react_agent import tool


# Env vars withheld from model-generated commands, so credentials never reach the agent's shell.
_SECRET_NAME = re.compile(
    r"KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|COOKIE|SESSION", re.IGNORECASE
)
_SECRET_PREFIXES = (
    "OPENAI_", "OPENROUTER_", "ANTHROPIC_", "TINKER_", "WANDB_", "AWS_", "AZURE_",
    "GOOGLE_", "GCP_", "HF_", "HUGGING", "GH_", "GITHUB_", "CLAUDE_", "CODEX_",
)


def _command_env() -> dict[str, str]:
    """Copy of os.environ without secret-looking variables (built per call: the
    agents set INPUT_FILE/OUTPUT_FILE for each run)."""
    return {
        name: value
        for name, value in os.environ.items()
        if not (_SECRET_NAME.search(name) or name.upper().startswith(_SECRET_PREFIXES))
    }


def create_bash_tool(working_dir: str, timeout: int = 120):
    """
    Create a bash execution tool for running commands.

    Commands run with the parent environment minus secrets (see _command_env).

    Args:
        working_dir: Directory where commands will be executed
        timeout: Command timeout in seconds
    """

    @tool(name="bash")
    def bash(command: str) -> str:
        """
        Execute a bash command in the working directory.
        Use this to run Python scripts, install packages, navigate files,
        or perform any shell operations.

        Args:
            command: The bash command to execute
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                env=_command_env(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}" if output else result.stderr
            if result.returncode != 0:
                output += f"\n[Exit code: {result.returncode}]"
            return output.strip() if output.strip() else "[Command completed with no output]"
        except subprocess.TimeoutExpired:
            return f"[ERROR] Command timed out after {timeout} seconds"
        except Exception as e:
            return f"[ERROR] Failed to execute command: {e}"

    return bash

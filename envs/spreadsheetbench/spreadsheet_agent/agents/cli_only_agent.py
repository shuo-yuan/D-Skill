# Modified from Trace2Skill (https://github.com/Qwen-Applications/Trace2Skill, Apache-2.0) for D-Skill; see NOTICE.
"""
CLI-Only Agent - Bash-only agent for spreadsheet manipulation.

This agent has access to only the bash tool, which is sufficient for:
- File system navigation (ls, cd, find, etc.)
- Executing Python scripts (python script.py or python -c "...")
- Reading Excel files (via Python one-liners or scripts)
- Any other shell operations
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "third_party", "trace2skill", "src"))

from react_agent import Tool

from .base import BaseSpreadsheetAgent
from ..tools import create_bash_tool
from ..system_prompts import load_full_system_prompt


class CLIOnlyAgent(BaseSpreadsheetAgent):
    """
    CLI-only agent that uses bash for all operations.

    This minimal agent demonstrates that a single bash tool is sufficient
    for file navigation, Python execution, and spreadsheet manipulation.

    Tools:
    - bash: Shell command execution (only tool)
    """

    def __init__(
        self,
        client,
        max_turns: int = 20,  # More turns since bash operations are more granular
        temperature: float = 0.0,
        verbose: bool = True,
        timeout: int = 120,
        log_dir: str | None = None,
        log_format: str = "markdown",
    ):
        super().__init__(client, max_turns, temperature, verbose, log_dir, log_format)
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "cli_only_agent"

    def get_system_template(self) -> str:
        return load_full_system_prompt("cli_only_full_system_v1.txt")

    def create_tools(self, working_dir: str) -> list[Tool]:
        return [
            create_bash_tool(working_dir, timeout=self.timeout),
        ]

    def build_task_prompt(self, context) -> str:
        """Build task prompt using official SpreadsheetBench format."""
        import os
        # Convert to absolute paths so agent knows exact locations
        working_dir = os.path.abspath(context.working_dir)
        input_file = os.path.abspath(context.input_file)
        output_file = os.path.abspath(context.output_file)
        
        return f"""Below is the spreadsheet manipulation question you need to solve:

### working_directory
{working_dir}

### instruction
{context.instruction}

### spreadsheet_path
{input_file}

### spreadsheet_content
{context.spreadsheet_content}

### instruction_type
{context.instruction_type}

### answer_position
{context.answer_position}

### output_path
{output_file}

---
**REMINDER**: You can ONLY access files within `{working_dir}`. Save output to the exact path: `{output_file}`
---

Solve the question and save the modified spreadsheet to the exact output_path shown above."""

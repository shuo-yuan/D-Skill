# Modified from Trace2Skill (https://github.com/Qwen-Applications/Trace2Skill, Apache-2.0) for D-Skill; see NOTICE.
"""
CLI Skill Preloaded Agent - Bash CLI agent with skill content pre-loaded in context.

The agent reads the SKILL.md files under skills_dir at initialization and embeds
the skill content (the first skill, in sorted order) directly into the system
prompt. The agent does not need to decide whether or when to read a skill file
— the full guidance is already available in context.
"""

import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "third_party", "trace2skill", "src"))

from react_agent import Tool

from .base import BaseSpreadsheetAgent
from ..tools import create_bash_tool
from ..system_prompts import render_full_system_prompt


@dataclass
class SkillMetadata:
    name: str
    description: str
    file_path: str


def extract_skill_metadata(skill_file: str) -> SkillMetadata | None:
    try:
        with open(skill_file, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError:
        return None

    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        return None

    frontmatter = frontmatter_match.group(1)
    name_match = re.search(r'^name:\s*["\']?([^"\'\n]+)["\']?\s*$', frontmatter, re.MULTILINE)
    desc_match = re.search(
        r'^description:\s*["\']?([^"\'\n]+)["\']?\s*$',
        frontmatter,
        re.MULTILINE,
    )
    if not name_match:
        return None

    return SkillMetadata(
        name=name_match.group(1).strip(),
        description=desc_match.group(1).strip() if desc_match else "",
        file_path=skill_file,
    )


def discover_skills(skills_dir: str) -> list[SkillMetadata]:
    skills = []
    if not os.path.exists(skills_dir):
        return skills

    for entry in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, entry)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if not (os.path.isdir(skill_dir) and os.path.exists(skill_file)):
            continue
        metadata = extract_skill_metadata(skill_file)
        if metadata is not None:
            skills.append(metadata)
    return skills


def read_skill_content(skill: SkillMetadata) -> str:
    """Read the full content of a skill file, stripping YAML frontmatter."""
    try:
        with open(skill.file_path, "r") as f:
            content = f.read()

        # Strip YAML frontmatter (already parsed into metadata)
        if content.startswith("---"):
            end = content.index("---", 3)
            content = content[end + 3:].lstrip("\n")

        return content
    except Exception:
        return ""


class CLISkillPreloadedAgent(BaseSpreadsheetAgent):
    """
    CLI agent with skill content pre-loaded in the system prompt.

    Skill content is read at initialization and embedded directly into the
    context. The agent follows skill guidance without needing to decide whether
    or when to read a skill file.

    Actions:
    - bash: Shell command execution

    Skills:
    - Discovered and fully loaded at initialization
    - Content embedded in system prompt, no runtime file reads needed
    """

    def __init__(
        self,
        client,
        skills_dir: str,
        max_turns: int = 20,
        temperature: float = 0.0,
        verbose: bool = True,
        timeout: int = 120,
        log_dir: str | None = None,
        log_format: str = "markdown",
    ):
        super().__init__(client, max_turns, temperature, verbose, log_dir, log_format)
        self.timeout = timeout
        self.skills_dir = os.path.abspath(skills_dir)

        # Discover skills and load their full content at initialization
        metadata_list = discover_skills(self.skills_dir)
        if not metadata_list:
            raise ValueError(
                f"No skills discovered in skills_dir: {self.skills_dir}"
            )
        self._skills: list[tuple[SkillMetadata, str]] = [
            (meta, read_skill_content(meta)) for meta in metadata_list
        ]

    @property
    def name(self) -> str:
        return "cli_skill_preloaded_agent"

    def get_system_template(self) -> str:
        # Load skill content and directory for the v1 template
        if self._skills:
            metadata, content = self._skills[0]
            skill_content = content
            skill_dir = os.path.dirname(os.path.abspath(metadata.file_path))
        else:
            skill_content = "(No skill loaded)"
            skill_dir = self.skills_dir

        return render_full_system_prompt(
            "cli_skill_preloaded_full_system_v1.txt",
            skill_content=skill_content,
            skill_dir=skill_dir,
        )

    def create_tools(self, working_dir: str) -> list[Tool]:
        return [
            create_bash_tool(working_dir, timeout=self.timeout),
        ]

    def build_task_prompt(self, context) -> str:
        """Build task prompt with absolute paths.

        There is no skills_directory field: the skill content is already
        embedded in the system prompt.
        """
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
**REMINDER**: Write files ONLY in `{working_dir}`. Save output to exact path: `{output_file}`
---

Solve the question and save the modified spreadsheet to the exact output_path shown above."""

    def get_available_skills(self) -> list[SkillMetadata]:
        """Get list of discovered skills with their loaded content."""
        return [meta for meta, _ in self._skills]

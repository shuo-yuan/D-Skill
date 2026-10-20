# Copied from microsoft/SkillOpt@0f76ab4 (MIT), skillopt/envs/alfworld/vendor/alfworld_prompts.py, which vendors SkillRL (Apache-2.0).
# Modified for D-Skill: load the templates from ./prompts instead of skillopt.prompts. See NOTICE.
# Vendored from SkillRL (Apache-2.0 License)
# Original: agent_system/environments/prompts/alfworld.py

import os


def load_prompt(name: str, env: str | None = None) -> str:
    # Same lookup result as skillopt.prompts.load_prompt for env='alfworld'.
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts", f"{name}.md")
    with open(path, encoding="utf-8") as f:
        return f.read()

ALFWORLD_TEMPLATE_NO_HIS = load_prompt("rollout_no_history", env="alfworld")
ALFWORLD_TEMPLATE = load_prompt("rollout_with_history", env="alfworld")
ALFWORLD_TEMPLATE_WITH_MEMORY = load_prompt("rollout_with_memory", env="alfworld")

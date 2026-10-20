"""D-Skill: distill a teacher agent into a skill document for a student agent.

Importing this package puts the vendored Trace2Skill (third_party/trace2skill)
and its src/ on sys.path, so `react_agent`, `src.react_agent`, `skill_evolver`
and `analysis` import as they do at the Trace2Skill repo root.
"""
import sys
from pathlib import Path

UPSTREAM = Path(__file__).resolve().parents[1] / "third_party" / "trace2skill"
for _p in (UPSTREAM, UPSTREAM / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

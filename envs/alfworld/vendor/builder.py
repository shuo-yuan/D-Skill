# Copied from microsoft/SkillOpt@0f76ab4 (MIT), skillopt/envs/alfworld/rollout.py.
# Modified for D-Skill: kept only build_alfworld_env and the gamefile resolution it uses; import paths; config path. See NOTICE.
"""Build the ALFWorld environment manager used by envs.alfworld.run_alfworld."""
from __future__ import annotations

import os


def _resolve_alfworld_gamefile(gamefile: str) -> str:
    path = os.path.expanduser(os.path.expandvars(str(gamefile)))
    if os.path.isabs(path):
        return path

    data_root = os.environ.get("ALFWORLD_DATA", "").strip()
    if not data_root:
        return path

    root = os.path.expanduser(os.path.expandvars(data_root))
    return os.path.abspath(os.path.join(root, path))


def _resolve_alfworld_gamefiles(gamefiles: list[str] | None) -> list[str] | None:
    if gamefiles is None:
        return None
    return [_resolve_alfworld_gamefile(gamefile) for gamefile in gamefiles]


# ── Environment builder ──────────────────────────────────────────────────────


def build_alfworld_env(
    env_num: int,
    eval_dataset: str = "eval_out_of_distribution",
    seed: int = 42,
    is_train: bool = False,
    specific_gamefiles: list[str] | None = None,
):
    """Build ALFWorld environment manager.

    Args:
        env_num: number of parallel environments
        eval_dataset: 'eval_in_distribution' or 'eval_out_of_distribution' or train
        seed: random seed
        is_train: whether to use training set

    Returns:
        env_manager: AlfWorldEnvironmentManager instance
    """
    from functools import partial

    from omegaconf import OmegaConf

    from envs.alfworld.vendor.alfworld_envs import build_alfworld_envs
    from envs.alfworld.vendor.alfworld_projection import alfworld_projection
    from envs.alfworld.vendor.env_manager import AlfWorldEnvironmentManager

    HERE = os.path.dirname(os.path.abspath(__file__))

    alf_config_path = os.path.join(HERE, "config_tw.yaml")
    env_kwargs = {"eval_dataset": eval_dataset}
    resolved_gamefiles = _resolve_alfworld_gamefiles(specific_gamefiles)

    envs = build_alfworld_envs(
        alf_config_path,
        seed=seed,
        env_num=env_num,
        group_n=1,
        is_train=is_train,
        env_kwargs=env_kwargs,
        resources_per_worker=None,
        gamefiles=resolved_gamefiles,
    )

    config = OmegaConf.create(
        {
            "env": {
                "history_length": 2,
                "env_name": "alfworld/AlfredTWEnv",
            }
        }
    )

    projection_f = partial(alfworld_projection)
    env_manager = AlfWorldEnvironmentManager(envs, projection_f, config)
    return env_manager

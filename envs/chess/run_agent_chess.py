"""Run chess puzzles through Claude Code with the chess MCP server.

Each episode is one `claude -p` call restricted to the chess tools
(--allowedTools, --disallowedTools BUILTIN_TOOLS; unlisted built-ins such
as ToolSearch stay reachable). The MCP server scores the episode into
results.jsonl. ANTHROPIC_API_KEY is dropped, so runs use the CLI login.

Usage:
  python -m envs.chess.run_agent_chess --harness cc --model claude-haiku-4-5 \
      --puzzles envs/chess/data/lichess_puzzles/puzzles_eval_400_2000.json \
      --run-tag ccsmoke --limit 3 --slots 3
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PYEXE = sys.executable          # the MCP server runs under this interpreter
REPO = Path(__file__).resolve().parents[2]

SYSTEM = """\
You are a chess tactics solver working inside a tool-use harness.
You interact with the position EXCLUSIVELY through the chess tools \
(hanging, threats, safety, simulate, board, line) and commit each \
move with the play tool. Analysis calls are budgeted per move; play \
is final.

Every tool takes a required `why` argument. Fill it honestly, max \
20 words, in this exact shape:
saw=<the piece/square/threat/motif you are reacting to> | \
test=<what this call should confirm or rule out>
Do not answer in prose — work with tools until the puzzle is over, \
then stop. If the environment asks you to call reflect after a play, \
always do so exactly once — including after the final move, before \
ending your reply.\
"""

TASK_FACTS = """\
This is a chess PUZZLE, not a full game: the entire puzzle is decided \
within your next 1-2 moves (your move now, then at most one forced \
opponent reply and your finishing move). Work out the best move at \
this short horizon only — deeper calculation is never needed. There \
is a clearly best move in this position.\
"""

BUILTIN_TOOLS = ("Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,"
                 "Task,NotebookEdit,TodoWrite,EnterWorktree,KillShell,"
                 "BashOutput,ExitPlanMode,ListMcpResources,"
                 "ReadMcpResource,Agent,Skill")
# "reflect" is no longer served; kept as in the paper runs' allow-list.
CHESS_TOOLS = ",".join(f"mcp__chess__{t}" for t in (
    "hanging", "threats", "safety", "simulate", "board", "line",
    "play", "reflect"))


def initial_obs(pz) -> str:
    import chess
    b = chess.Board(pz["FEN"])
    moves = pz["Moves"].split()
    b.push(chess.Move.from_uci(moves[0]))
    sys.path.insert(0, str(REPO))
    from envs.chess import chess_query
    legal = sorted(b.san(m) for m in b.legal_moves)
    return (f"Position (FEN): {b.fen()}\n\n"
            f"Board (uppercase = White, lowercase = Black, rank 8 at "
            f"top):\n{b}\n\n"
            f"You are playing: {'White' if b.turn else 'Black'}\n\n"
            f"{chess_query.material_line(b, b.turn).capitalize()}\n\n"
            f"Legal moves: {', '.join(legal)}")


def run_watched(cmd, resfile: Path, pid: str, timeout: int, out_path,
                grace: float = 8.0, **popen_kw):
    """Run `cmd`, terminating it `grace` seconds after this puzzle's result
    row appears in `resfile`. Returns (returncode, timed_out)."""
    import subprocess as sp
    import time as _t
    needle = f'"puzzle": "{pid}"'
    with open(out_path, "w") as out:
        p = sp.Popen(cmd, stdout=out, stderr=sp.STDOUT, **popen_kw)
        t0 = _t.time()
        seen_at = None
        while True:
            rc = p.poll()
            if rc is not None:
                return rc, False
            now = _t.time()
            if now - t0 > timeout:
                p.terminate()
                try:
                    p.wait(10)
                except sp.TimeoutExpired:
                    p.kill()
                return -1, True
            if seen_at is None and int(now) % 2 == 0:
                try:
                    if needle in resfile.read_text():
                        seen_at = now
                except FileNotFoundError:
                    pass
            if seen_at is not None and now - seen_at > grace:
                p.terminate()
                try:
                    p.wait(10)
                except sp.TimeoutExpired:
                    p.kill()
                return 0, False
            _t.sleep(0.5)


def run_episode_cc(pz, args, outdir: Path, resfile: Path):
    mcp_cfg = {"mcpServers": {"chess": {
        "command": PYEXE, "args": ["-m", "envs.chess.chess_mcp"],
        "env": {"HD_MCP_FEN": pz["FEN"], "HD_MCP_MOVES": pz["Moves"],
                "HD_MCP_PID": pz["PuzzleId"],
                "HD_MCP_RATING": str(pz.get("Rating", 0)),
                "HD_MCP_OUT": str(resfile),
                "HD_MCP_BUDGET": str(args.budget),
                "PYTHONPATH": str(REPO)}}}}
    cfgfile = outdir / f"mcp_{pz['PuzzleId']}.json"
    cfgfile.write_text(json.dumps(mcp_cfg))
    prompt = (f"{TASK_FACTS}\n\n{initial_obs(pz)}\n\n"
              "Solve the puzzle now using the chess tools; commit each "
              "move with play.")
    skill = ""
    if args.skill_file:
        skill = ("\n\n## Skill\n"
                 + Path(args.skill_file).read_text().strip())
    import os as _os
    env = {k: v for k, v in _os.environ.items()
           if k != "ANTHROPIC_API_KEY"}         # CLI login, not an API key
    if _os.environ.get("HD_CC_CONFIG_DIR"):          # optional separate CLI profile
        env["CLAUDE_CONFIG_DIR"] = _os.environ["HD_CC_CONFIG_DIR"]
    cmd = ["claude", "-p", prompt,
           "--model", args.model,
           *(["--effort", args.effort]
             if args.effort != "default" else []),
           "--system-prompt", SYSTEM + skill,
           "--mcp-config", str(cfgfile), "--strict-mcp-config",
           "--allowedTools", CHESS_TOOLS,
           "--disallowedTools", BUILTIN_TOOLS,
           "--max-turns", str(args.max_turns),
           "--output-format", "json"]
    t0 = time.time()
    out_path = outdir / f"stdout_{pz['PuzzleId']}.txt"
    rc, timed_out = run_watched(cmd, resfile, pz["PuzzleId"],
                                args.timeout, out_path,
                                cwd=str(outdir), env=env)
    meta = {"rc": rc, "timeout": timed_out}
    try:
        j = json.loads(out_path.read_text())
        meta.update({k: j.get(k) for k in
                     ("total_cost_usd", "num_turns", "is_error")})
    except (json.JSONDecodeError, FileNotFoundError):
        try:
            meta["stdout_tail"] = out_path.read_text()[-400:]
        except FileNotFoundError:
            pass
    meta["wall_s"] = round(time.time() - t0, 1)
    (outdir / f"meta_{pz['PuzzleId']}.json").write_text(json.dumps(meta))
    return pz["PuzzleId"], meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", choices=["cc"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--puzzles", required=True)
    ap.add_argument("--run-tag", required=True)
    ap.add_argument("--skill-file", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--slots", type=int, default=4)
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--max-turns", type=int, default=40)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--effort", default="default",
                    help="claude --effort passthrough (omitted at "
                         "'default')")
    args = ap.parse_args()

    puzzles = json.load(open(args.puzzles))
    if args.limit:
        puzzles = puzzles[:args.limit]
    base = (REPO / "runs" /
            f"agentchess_{args.harness}_{args.model}_{args.run_tag}")
    base.mkdir(parents=True, exist_ok=True)
    resfile = base / "results.jsonl"
    done = set()
    if resfile.exists():
        done = {json.loads(l)["puzzle"] for l in open(resfile)}
    todo = [p for p in puzzles if p["PuzzleId"] not in done]
    print(f"agentchess {args.harness}/{args.model} [{args.run_tag}]: "
          f"{len(done)} done, {len(todo)} to run", flush=True)
    k = len(done)
    with ThreadPoolExecutor(max_workers=args.slots) as ex:
        futs = [ex.submit(run_episode_cc, p, args, base, resfile)
                for p in todo]
        for f in as_completed(futs):
            pid, meta = f.result()
            k += 1
            print(f"[{k}/{len(puzzles)}] {pid} rc={meta.get('rc')} "
                  f"turns={meta.get('num_turns')} "
                  f"{meta['wall_s']}s", flush=True)
    res = [json.loads(l) for l in open(resfile)] if resfile.exists() else []
    n = len(res)
    s = sum(r["solved"] for r in res)
    fm = sum(r["first_move_ok"] for r in res)
    print(f"FINAL {args.harness}/{args.model}: n={n} "
          f"strict={s}/{n} first-move={fm}/{n}")


if __name__ == "__main__":
    main()

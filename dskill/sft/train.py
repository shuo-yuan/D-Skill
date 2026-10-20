"""SFT the student on the teacher rollouts via the Tinker API (LoRA).

Logs a sampler checkpoint per epoch (plus optional mid-epoch ones via
--save-steps / --save-episodes) to --out; each is evaluated separately
through dskill.llm.tinker_proxy.

    python -m dskill.sft.train --base-model <slug> --epochs 3 --rank 16
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def load_examples(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def init_wandb(args, n_examples: int, n_trainable_tok: int):
    """Optional W&B run; None if HD_WANDB=0, wandb is missing or no key."""
    if os.environ.get("HD_WANDB", "1") == "0":
        return None
    try:
        import wandb
    except ImportError:
        print("[sft] wandb not installed — skipping logging", flush=True)
        return None
    if not (os.environ.get("WANDB_API_KEY") or os.environ.get("WANDB_MODE")):
        print("[sft] no WANDB_API_KEY — skipping logging", flush=True)
        return None
    run = wandb.init(
        project=os.environ.get("WANDB_PROJECT", "dskill-sft"),
        name=os.environ.get("WANDB_NAME") or f"sft-{Path(args.data).stem}",
        config={"base_model": args.base_model, "rank": args.rank,
                "epochs": args.epochs, "batch_size": args.batch_size,
                "lr": args.lr, "max_len": args.max_len, "seed": args.seed,
                "data": str(args.data), "n_examples": n_examples,
                "trainable_tokens": n_trainable_tok,
                "arm": "sft-weights", "gt_free": "filtered" not in str(args.data)},
        tags=["dskill", "sft", "tinker"])
    print(f"[sft] wandb run: {run.url}", flush=True)
    return run


def render(ex: dict, tok, max_len: int) -> tuple[list[int], list[float]]:
    """messages -> (token_ids, per-token loss weights), 1.0 on assistant turns.

    Message spans come from templating growing prefixes (templates reject a
    lone message), so the chat template must be append-only.
    """
    msgs = [{"role": m["role"], "content": m["content"]} for m in ex["messages"]]
    flags = [bool(m.get("loss")) for m in ex["messages"]]

    # Mask by char offsets: rendered text is prefix-stable, tokens are not.
    spans: list[tuple[int, int]] = []
    prev_len = 0
    for k in range(2, len(msgs) + 1):          # template needs >=1 user turn
        text_k = tok.apply_chat_template(msgs[:k], tokenize=False)
        spans.append((prev_len, len(text_k)))
        prev_len = len(text_k)
    full = tok.apply_chat_template(msgs, tokenize=False)

    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    ids = enc["input_ids"]
    offs = enc["offset_mapping"]

    # message k (1-indexed into msgs) owns spans[k-2] for k >= 2
    keep = [spans[k - 2] for k in range(2, len(msgs) + 1) if flags[k - 1]]
    w = []
    for (s, e) in offs:
        mid = (s + e) / 2 if e > s else s
        w.append(1.0 if any(a <= mid < b for a, b in keep) else 0.0)
    return ids[:max_len], w[:max_len]


def lr_at(step: int, total: int, peak: float, warmup: float = 0.05) -> float:
    wu = max(1, int(total * warmup))
    if step < wu:
        return peak * step / wu
    frac = (step - wu) / max(1, total - wu)
    return peak * max(0.05, 1.0 - frac)          # linear decay to 5%


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path,
                    default=REPO / "runs/sft/teacher_sft.jsonl")
    ap.add_argument("--base-model", required=True,
                    help="e.g. Qwen/Qwen3.6-35B-A3B (decide before running)")
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--max-len", type=int, default=16384,
                    help="16k covers 96%% of episodes; 8k silently drops the "
                         "long recovery traces worth cloning")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ttl-seconds", type=int, default=7*24*3600,
                    help="checkpoint lifetime; the API default expires in "
                         "hours, which breaks later re-evaluation")
    ap.add_argument("--out", type=Path, default=REPO / "runs/sft/run_log.jsonl")
    ap.add_argument("--save-steps", default="",
                    help="comma-separated GLOBAL step numbers at which to "
                         "save extra mid-epoch sampler checkpoints "
                         "(within-epoch learning curve)")
    ap.add_argument("--group-shuffle", action="store_true",
                    help="shuffle at the EPISODE level (examples carry an "
                         "'episode' field), keeping turn order within an "
                         "episode -- for per-turn corpora")
    ap.add_argument("--save-episodes", default="",
                    help="comma-separated distinct-episode counts at which "
                         "to save extra sampler checkpoints within "
                         "--save-episodes-epoch (needs --group-shuffle)")
    ap.add_argument("--save-episodes-epoch", type=int, default=1)
    args = ap.parse_args()

    import tinker
    from tinker import types

    exs = load_examples(args.data)
    sc = tinker.ServiceClient()
    tc = sc.create_lora_training_client(base_model=args.base_model,
                                        rank=args.rank)
    tok = tc.get_tokenizer()

    data, truncated, n_tok = [], 0, 0
    ep_ids = []          # episode id per datum (per-turn corpora)
    for ex in exs:
        ids, w = render(ex, tok, args.max_len)
        if len(ids) < 16:
            continue
        if sum(w[1:]) == 0:                       # nothing trainable left
            continue
        truncated += int(len(ids) == args.max_len)
        n_tok += int(sum(w[1:]))
        data.append(types.Datum(
            model_input=types.ModelInput.from_ints(ids[:-1]),
            loss_fn_inputs={"weights": w[1:], "target_tokens": ids[1:]}))
        ep_ids.append(ex.get("episode", len(data) - 1))
    print(f"[sft] {len(data)} examples ready "
          f"({truncated} truncated at {args.max_len} tok, "
          f"{n_tok:,} trainable tokens)", flush=True)
    run = init_wandb(args, len(data), n_tok)

    steps_per_epoch = (len(data) + args.batch_size - 1) // args.batch_size
    total = steps_per_epoch * args.epochs
    args.out.parent.mkdir(parents=True, exist_ok=True)
    logf = args.out.open("a")
    rng = random.Random(args.seed)
    mid_saves = {int(x) for x in args.save_steps.split(",") if x.strip()}
    ep_saves = sorted(int(x) for x in args.save_episodes.split(",") if x.strip())
    groups: dict = {}
    for d, g in zip(data, ep_ids):
        groups.setdefault(g, []).append(d)

    def shuffle_epoch():
        """Shuffle; --group-shuffle shuffles episodes, keeping turn order."""
        if args.group_shuffle:
            order = list(groups)
            rng.shuffle(order)
            return ([d for g in order for d in groups[g]],
                    [g for g in order for _ in groups[g]])
        rng.shuffle(data)
        return data, list(range(len(data)))

    step = 0

    for ep in range(1, args.epochs + 1):
        data, ep_of = shuffle_epoch()
        pending_ep_saves = list(ep_saves) if ep == args.save_episodes_epoch else []
        losses = []
        for i in range(0, len(data), args.batch_size):
            lr = lr_at(step, total, args.lr)
            fb = tc.forward_backward(data[i:i + args.batch_size],
                                     loss_fn="cross_entropy")
            tc.optim_step(types.AdamParams(learning_rate=lr))
            step += 1
            if step in mid_saves:
                ck = tc.save_weights_for_sampler(
                    name=f"sft-ep{ep}-s{step}",
                    ttl_seconds=args.ttl_seconds).result()
                mrec = {"epoch": ep, "step": step, "mid": True,
                        "examples_seen": min(step * args.batch_size,
                                             len(data) * ep),
                        "checkpoint": ck.path}
                logf.write(json.dumps(mrec) + "\n")
                logf.flush()
                print(f"[sft] mid-save step {step} -> {ck.path}",
                      flush=True)
            # --save-episodes: save once this epoch has seen >= N episodes
            seen_eps = len(set(ep_of[:i + args.batch_size]))
            while pending_ep_saves and seen_eps >= pending_ep_saves[0]:
                thr = pending_ep_saves.pop(0)
                ck = tc.save_weights_for_sampler(
                    name=f"sft-ep{ep}-n{thr}",
                    ttl_seconds=args.ttl_seconds).result()
                mrec = {"epoch": ep, "step": step, "mid": True,
                        "episodes_seen": thr,
                        "examples_seen": min(i + args.batch_size, len(data)),
                        "checkpoint": ck.path}
                logf.write(json.dumps(mrec) + "\n")
                logf.flush()
                print(f"[sft] episode-save {thr} eps (step {step}) -> "
                      f"{ck.path}", flush=True)
            try:
                loss = float(fb.result().metrics.get("loss:sum", 0))
                losses.append(loss)
                if run:
                    run.log({"train/loss": loss, "train/lr": lr,
                             "train/epoch": ep}, step=step)
            except Exception:                      # noqa: BLE001
                pass
            if step % 10 == 0:
                print(f"[sft] epoch {ep} step {step}/{total} "
                      f"loss~{sum(losses[-10:])/max(1,len(losses[-10:])):.4f}",
                      flush=True)

        ck = tc.save_weights_for_sampler(
            name=f"sft-ep{ep}", ttl_seconds=args.ttl_seconds).result()
        rec = {"epoch": ep, "step": step, "checkpoint": ck.path,
               "mean_loss": sum(losses) / max(1, len(losses))}
        # Training state too: sampler weights alone cannot be resumed.
        try:
            st = tc.save_state(name=f"sft-state-ep{ep}",
                               ttl_seconds=args.ttl_seconds).result()
            rec["state_path"] = getattr(st, "path", None)
        except Exception as exc:                          # noqa: BLE001
            print(f"[sft] save_state failed (non-fatal): {exc!r}", flush=True)
        if run:
            rec["wandb_run_id"] = run.id
            run.log({"epoch/mean_loss": rec["mean_loss"],
                     "epoch/index": ep}, step=step)
        print(f"[sft] epoch {ep} done -> {ck.path}", flush=True)

        logf.write(json.dumps(rec) + "\n")
        logf.flush()

    print("[sft] ALL DONE — report the full epoch curve, not the best point")


if __name__ == "__main__":
    main()

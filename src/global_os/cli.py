"""CLI: gos goal|events|audit|mission — Operator Edition supervised path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from global_os.runtime.local_store import FileRuntime, dump_json


def _load_goal_json(path: Path) -> dict[str, Any]:
    """Load Goal JSON; skip leading full-line # comments (operator convenience)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("#")):
        lines.pop(0)
    raw = json.loads("\n".join(lines))
    if not isinstance(raw, dict):
        raise SystemExit(f"error: goal file must be a JSON object: {path}")
    return raw


def cmd_goal_create(args: argparse.Namespace) -> int:
    rt = FileRuntime(root=Path(args.root) if args.root else None)
    draft = _load_goal_json(Path(args.file))
    goal = rt.goals.create(draft)
    rt.save()
    print(dump_json(goal))
    return 0


def cmd_goal_show(args: argparse.Namespace) -> int:
    rt = FileRuntime(root=Path(args.root) if args.root else None)
    version = int(args.version) if args.version else None
    goal = rt.goals.get(args.goal_id, version=version)
    print(dump_json(goal))
    return 0


def cmd_events_tail(args: argparse.Namespace) -> int:
    rt = FileRuntime(root=Path(args.root) if args.root else None)
    events = rt.ledger.list_events(goal_id=args.goal_id)
    for event in events[-args.n :]:
        print(json.dumps(event, ensure_ascii=False))
    return 0


def cmd_events_replay(args: argparse.Namespace) -> int:
    """Time-travel: rebuild status projection at event index (ADR-0013 / LangGraph UX)."""
    from global_os.runtime.events.replay import EventReplayEngine

    rt = FileRuntime(root=Path(args.root) if args.root else None)
    engine = EventReplayEngine(rt.ledger)
    if args.compare is not None:
        out = engine.compare_at(
            index_a=args.at,
            index_b=args.compare,
            goal_id=args.goal_id,
        )
    else:
        out = engine.rebuild_status_projection(
            goal_id=args.goal_id,
            until_index=args.at,
            record_rebuild_event=False,
        )
    print(dump_json(out))
    return 0


def cmd_audit_repo(args: argparse.Namespace) -> int:
    from global_os.world.tools import run_repo_audit

    report = run_repo_audit(Path(args.path))
    print(dump_json(report))
    return 0


def _gos_root(args: argparse.Namespace) -> Path:
    return Path(args.root) if getattr(args, "root", None) else Path.cwd() / ".gos"


def cmd_mission_start(args: argparse.Namespace) -> int:
    from global_os.runtime.preprod import SupervisedMissionError, start_mission

    draft = _load_goal_json(Path(args.goal))
    try:
        out = start_mission(
            draft,
            target_path=args.target,
            gos_root=_gos_root(args),
            budget_usd=float(args.budget_usd),
            budget_tokens=int(args.budget_tokens),
        )
    except SupervisedMissionError as exc:
        print(f"error: {exc}")
        return 2
    print(dump_json(out))
    return 0


def cmd_mission_status(args: argparse.Namespace) -> int:
    from global_os.runtime.preprod import SupervisedMissionError, status_mission

    try:
        out = status_mission(gos_root=_gos_root(args), run_id=args.run_id)
    except SupervisedMissionError as exc:
        print(f"error: {exc}")
        return 2
    print(dump_json(out))
    return 0


def cmd_mission_pause(args: argparse.Namespace) -> int:
    from global_os.runtime.preprod import SupervisedMissionError, pause_mission

    try:
        out = pause_mission(gos_root=_gos_root(args), run_id=args.run_id)
    except SupervisedMissionError as exc:
        print(f"error: {exc}")
        return 2
    print(dump_json(out))
    return 0


def cmd_mission_resume(args: argparse.Namespace) -> int:
    from global_os.runtime.preprod import SupervisedMissionError, resume_mission

    try:
        out = resume_mission(gos_root=_gos_root(args), run_id=args.run_id)
    except SupervisedMissionError as exc:
        print(f"error: {exc}")
        return 2
    print(dump_json(out))
    return 0


def cmd_mission_cancel(args: argparse.Namespace) -> int:
    from global_os.runtime.preprod import SupervisedMissionError, cancel_mission

    try:
        out = cancel_mission(gos_root=_gos_root(args), run_id=args.run_id)
    except SupervisedMissionError as exc:
        print(f"error: {exc}")
        return 2
    print(dump_json(out))
    return 0


def cmd_mission_deliver(args: argparse.Namespace) -> int:
    from global_os.runtime.preprod import SupervisedMissionError, deliver_mission

    try:
        out = deliver_mission(gos_root=_gos_root(args), run_id=args.run_id)
    except SupervisedMissionError as exc:
        print(f"error: {exc}")
        return 2
    print(dump_json(out))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gos", description="Global OS CLI")
    parser.add_argument(
        "--root",
        default=None,
        help="Runtime root (default: ./.gos)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    goal = sub.add_parser("goal", help="Goal Contract operations")
    goal_sub = goal.add_subparsers(dest="goal_command", required=True)

    create = goal_sub.add_parser("create", help="Create goal from JSON file")
    create.add_argument("file", help="Path to goal JSON")
    create.set_defaults(func=cmd_goal_create)

    show = goal_sub.add_parser("show", help="Show goal by id")
    show.add_argument("goal_id")
    show.add_argument("--version", default=None)
    show.set_defaults(func=cmd_goal_show)

    events = sub.add_parser("events", help="Event ledger")
    events_sub = events.add_subparsers(dest="events_command", required=True)
    tail = events_sub.add_parser("tail", help="Print recent events")
    tail.add_argument("--goal-id", dest="goal_id", default=None)
    tail.add_argument("-n", type=int, default=20)
    tail.set_defaults(func=cmd_events_tail)

    replay = events_sub.add_parser(
        "replay", help="Rebuild status projection at --at index (time-travel)"
    )
    replay.add_argument("--goal-id", dest="goal_id", default=None)
    replay.add_argument(
        "--at", type=int, required=True, help="Exclusive end event index"
    )
    replay.add_argument(
        "--compare",
        type=int,
        default=None,
        help="Optional second index to diff projections",
    )
    replay.set_defaults(func=cmd_events_replay)

    audit = sub.add_parser("audit", help="Read-only repository audit")
    audit.add_argument("path", nargs="?", default=".", help="Repo path to audit")
    audit.set_defaults(func=cmd_audit_repo)

    mission = sub.add_parser(
        "mission",
        help="PREPROD_SUPERVISED mission (Goal→Gateway→Achiever→Delivery)",
    )
    mission_sub = mission.add_subparsers(dest="mission_command", required=True)

    m_start = mission_sub.add_parser("start", help="Start supervised mission from Goal JSON")
    m_start.add_argument("--goal", required=True, help="Path to Goal Contract JSON")
    m_start.add_argument(
        "--target",
        default=".",
        help="Read-only workspace path for sandbox observe tools",
    )
    m_start.add_argument("--budget-usd", default="15.0")
    m_start.add_argument("--budget-tokens", default="50000")
    m_start.set_defaults(func=cmd_mission_start)

    for name, fn, help_text in (
        ("status", cmd_mission_status, "Show mission status"),
        ("pause", cmd_mission_pause, "Pause active mission"),
        ("resume", cmd_mission_resume, "Resume paused / interrupted mission"),
        ("cancel", cmd_mission_cancel, "Cancel mission"),
        ("deliver", cmd_mission_deliver, "Print delivery package"),
    ):
        p = mission_sub.add_parser(name, help=help_text)
        p.add_argument("--run-id", default=None)
        p.set_defaults(func=fn)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

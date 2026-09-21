"""CLI: gos goal create|show ; gos events tail."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from global_os.runtime.local_store import FileRuntime, dump_json


def cmd_goal_create(args: argparse.Namespace) -> int:
    rt = FileRuntime()
    draft = json.loads(Path(args.file).read_text(encoding="utf-8"))
    goal = rt.goals.create(draft)
    rt.save()
    print(dump_json(goal))
    return 0


def cmd_goal_show(args: argparse.Namespace) -> int:
    rt = FileRuntime()
    version = int(args.version) if args.version else None
    goal = rt.goals.get(args.goal_id, version=version)
    print(dump_json(goal))
    return 0


def cmd_events_tail(args: argparse.Namespace) -> int:
    rt = FileRuntime()
    events = rt.ledger.list_events(goal_id=args.goal_id)
    for event in events[-args.n :]:
        print(json.dumps(event, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gos", description="Global OS CLI")
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

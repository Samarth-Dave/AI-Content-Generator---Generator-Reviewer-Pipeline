from __future__ import annotations

import argparse
import json

from orchestrator_v2 import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Eklavya content pipeline")
    parser.add_argument("--grade", type=int, required=True)
    parser.add_argument("--topic", type=str, required=True)
    parser.add_argument("--user-id", type=str, default="default_user")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_pipeline(grade=args.grade, topic=args.topic, user_id=args.user_id)
    print(json.dumps(result.model_dump(mode="json", by_alias=True), indent=2))


if __name__ == "__main__":
    main()

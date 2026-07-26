from __future__ import annotations

import argparse
import json

from orchestrator import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Eklavya content pipeline")
    parser.add_argument("--grade", type=int, required=True)
    parser.add_argument("--topic", type=str, required=True)
    parser.add_argument("--no-rereview", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_pipeline(
        grade=args.grade,
        topic=args.topic,
        re_review_refinement=not args.no_rereview,
    )
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()

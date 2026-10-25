"""Research Hippo v0.1.0 entry point."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research Hippo AI Research Assistant")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--cli", action="store_true", help="run the Rich CLI")
    mode.add_argument("--tui", action="store_true", help="run the Textual TUI (default)")
    parser.add_argument("--mock", action="store_true", help="use deterministic demo data without an API")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.cli:
        from ui.cli import start_cli

        return start_cli(mock=args.mock)

    from ui.tui.app import start_tui

    start_tui(mock=args.mock)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

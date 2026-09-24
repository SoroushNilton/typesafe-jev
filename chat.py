"""Interactive back-and-forth with Jev.

Jev doesn't chat: each turn you give it a *state* (text) and it answers a fixed
set of typed questions about it. Load questions from a JSON file, then type
states and read the decisions.

    python chat.py                          # uses questions/support_ticket.json
    python chat.py questions/my_task.json

Commands:  :q quit | :load <file> reload questions | :show list questions | :raw toggle raw JSON
"""

import json
import sys
from pathlib import Path

from jev import Jev

# DEFAULT_QUESTIONS = Path(__file__).parent / "questions" / "support_ticket.json"
DEFAULT_QUESTIONS = Path(__file__).parent / "questions" / "email_triage.json"


def load_questions(path: Path) -> dict:
    questions = json.loads(path.read_text())
    print(f"Loaded {len(questions)} question(s) from {path}")
    return questions


def fmt(value) -> str:
    return f"{value:.3f}" if isinstance(value, float) else str(value)


def render(response: dict) -> None:
    answers = response.get("answers", response)
    for name, ans in answers.items():
        if not isinstance(ans, dict):
            print(f"  {name}: {fmt(ans)}")
            continue
        main = {k: v for k, v in ans.items() if k != "probabilities"}
        print(f"  {name}: " + ", ".join(f"{k}={fmt(v)}" for k, v in main.items()))
        probs = ans.get("probabilities")
        if isinstance(probs, dict):
            for opt, p in sorted(probs.items(), key=lambda kv: -kv[1]):
                print(f"      {opt:<16} {p:6.1%}  {'#' * round(p * 30)}")
    cost = response.get("usage", {}).get("cost")
    if cost is not None:
        print(f"  (cost ${cost:.8f})")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_QUESTIONS
    questions = load_questions(path)
    raw = False

    with Jev() as jev:
        print(f"Model: {jev.model}. Type a state, or :q to quit.\n")
        while True:
            try:
                line = input("state> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            if line == ":q":
                break
            if line == ":raw":
                raw = not raw
                print(f"raw output {'on' if raw else 'off'}")
                continue
            if line == ":show":
                print(json.dumps(questions, indent=2))
                continue
            if line.startswith(":load"):
                path = Path(line.split(maxsplit=1)[1]) if " " in line else path
                questions = load_questions(path)
                continue

            try:
                response = jev.decide({"text": line}, questions)
            except Exception as e:
                print(f"  error: {e}")
                continue
            print(json.dumps(response, indent=2)) if raw else render(response)
            print()


if __name__ == "__main__":
    main()

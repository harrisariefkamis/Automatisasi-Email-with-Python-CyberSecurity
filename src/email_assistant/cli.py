"""Command line JSON email triage."""

import argparse
import json
from pathlib import Path

from email_assistant.core import as_jsonable, triage_email


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage satu email JSON secara lokal.")
    parser.add_argument("email_json", help="Path JSON berisi from, subject, body, dan headers opsional")
    args = parser.parse_args()
    email = json.loads(Path(args.email_json).read_text(encoding="utf-8"))
    print(json.dumps(as_jsonable(triage_email(email)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

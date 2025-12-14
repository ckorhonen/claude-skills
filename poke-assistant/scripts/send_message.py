#!/usr/bin/env python3
"""Send messages to Poke assistant via webhook API."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

POKE_WEBHOOK_URL = "https://poke.com/api/v1/inbound-sms/webhook"


def get_api_key():
    """Get API key from environment."""
    key = os.environ.get("POKE_API_KEY")
    if not key:
        print("Error: POKE_API_KEY environment variable not set", file=sys.stderr)
        print(
            "Get your API key from https://poke.com/settings (Advanced section)",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def send_message(message: str, api_key: str) -> bool:
    """Send message to Poke webhook.

    Returns True on success, exits with error code on failure.
    """
    data = json.dumps({"message": message}).encode("utf-8")
    req = urllib.request.Request(
        POKE_WEBHOOK_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        print(f"Error: API returned {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(2)
    except urllib.error.URLError as e:
        print(f"Error: Network error: {e.reason}", file=sys.stderr)
        sys.exit(3)


def main():
    parser = argparse.ArgumentParser(
        description="Send a message to Poke assistant via webhook"
    )
    parser.add_argument("-m", "--message", help="Message to send to Poke")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )
    args = parser.parse_args()

    # Get message from arg or stdin
    message = args.message
    if not message and not sys.stdin.isatty():
        message = sys.stdin.read().strip()

    if not message:
        print(
            "Error: No message provided. Use -m 'message' or pipe to stdin.",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = get_api_key()

    if args.verbose:
        print(f"Sending message to Poke ({len(message)} chars)...", file=sys.stderr)

    if send_message(message, api_key):
        print("Message sent to Poke")


if __name__ == "__main__":
    main()

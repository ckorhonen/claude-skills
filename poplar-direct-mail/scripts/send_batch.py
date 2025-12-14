#!/usr/bin/env python3
"""Send batch mailings from a CSV file via Poplar API.

CSV Format:
    Required columns: address_1, city, state, postal_code
    Optional columns: first_name, last_name, full_name, address_2, company
    Custom columns: Any additional columns become merge tags

Usage:
    python send_batch.py --csv recipients.csv --campaign-id CAMPAIGN_ID

Environment:
    POPLAR_API_TOKEN: Your Poplar API token
"""

import os
import sys
import csv
import time
import json
import argparse
import requests
from typing import Generator
from datetime import datetime

POPLAR_API_URL = "https://api.heypoplar.com/v1"

# Columns that map to recipient fields (not merge tags)
RECIPIENT_FIELDS = {
    "first_name", "last_name", "full_name", "company",
    "address_1", "address_2", "city", "state", "postal_code",
    "email", "identifier"
}


def read_recipients(csv_path: str) -> Generator[dict, None, None]:
    """Read recipients from CSV file.

    Args:
        csv_path: Path to CSV file

    Yields:
        Dictionary with 'recipient' and 'merge_tags' keys
    """
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            # Build recipient object
            recipient = {}
            merge_tags = {}

            for key, value in row.items():
                if not key or not value:
                    continue

                key_lower = key.lower().strip()

                if key_lower in RECIPIENT_FIELDS:
                    recipient[key_lower] = value.strip()
                else:
                    # Custom column becomes merge tag
                    merge_tags[key.strip()] = value.strip()

            # Validate required fields
            if not recipient.get("address_1"):
                print(f"Warning: Row {row_num} missing address_1, skipping")
                continue
            if not recipient.get("city"):
                print(f"Warning: Row {row_num} missing city, skipping")
                continue
            if not recipient.get("state"):
                print(f"Warning: Row {row_num} missing state, skipping")
                continue
            if not recipient.get("postal_code"):
                print(f"Warning: Row {row_num} missing postal_code, skipping")
                continue

            yield {
                "row_num": row_num,
                "recipient": recipient,
                "merge_tags": merge_tags
            }


def send_batch(
    csv_path: str,
    campaign_id: str,
    creative_id: str = None,
    delay: float = 0.1,
    dry_run: bool = False,
    max_records: int = None
) -> tuple[int, int, list]:
    """Send batch mailings from CSV.

    Args:
        csv_path: Path to CSV file
        campaign_id: Campaign ID from Poplar
        creative_id: Optional creative ID
        delay: Delay between requests in seconds
        dry_run: If True, don't actually send mailings
        max_records: Maximum number of records to process

    Returns:
        Tuple of (success_count, error_count, errors_list)
    """
    token = os.environ.get("POPLAR_API_TOKEN")
    if not token:
        raise ValueError("POPLAR_API_TOKEN environment variable not set")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    success_count = 0
    error_count = 0
    errors = []
    processed = 0

    for record in read_recipients(csv_path):
        if max_records and processed >= max_records:
            print(f"\nReached max records limit ({max_records})")
            break

        processed += 1
        row_num = record["row_num"]
        recipient = record["recipient"]
        merge_tags = record["merge_tags"]

        name = recipient.get("full_name") or \
               f"{recipient.get('first_name', '')} {recipient.get('last_name', '')}".strip() or \
               "Unknown"

        if dry_run:
            print(f"[DRY RUN] Row {row_num}: Would send to {name}")
            success_count += 1
            continue

        payload = {
            "campaign_id": campaign_id,
            "recipient": recipient
        }

        if creative_id:
            payload["creative_id"] = creative_id
        if merge_tags:
            payload["merge_tags"] = merge_tags

        try:
            response = requests.post(
                f"{POPLAR_API_URL}/mailing",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            success_count += 1
            print(f"Row {row_num}: Sent to {name} (ID: {result['id']})")

        except requests.exceptions.HTTPError as e:
            error_count += 1
            error_msg = str(e)
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = json.dumps(error_detail)
                except json.JSONDecodeError:
                    error_msg = e.response.text

            errors.append({
                "row": row_num,
                "recipient": name,
                "error": error_msg
            })
            print(f"Row {row_num}: ERROR sending to {name} - {error_msg}")

        except requests.exceptions.RequestException as e:
            error_count += 1
            errors.append({
                "row": row_num,
                "recipient": name,
                "error": str(e)
            })
            print(f"Row {row_num}: ERROR sending to {name} - {e}")

        if delay > 0:
            time.sleep(delay)

    return success_count, error_count, errors


def main():
    parser = argparse.ArgumentParser(
        description="Send batch Poplar mailings from CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format:
    Required columns: address_1, city, state, postal_code
    Optional: first_name, last_name, full_name, address_2, company
    Custom columns become merge tags (e.g., promo_code, expiration_date)

Example CSV:
    first_name,last_name,address_1,city,state,postal_code,promo_code
    Jane,Smith,123 Main St,Austin,TX,78701,SAVE20
    John,Doe,456 Oak Ave,Denver,CO,80202,SAVE25

Examples:
    # Dry run to preview
    python send_batch.py --csv recipients.csv --campaign-id abc123 --dry-run

    # Send first 10 as test
    python send_batch.py --csv recipients.csv --campaign-id abc123 --max 10

    # Full batch with slower rate
    python send_batch.py --csv recipients.csv --campaign-id abc123 --delay 0.5
        """
    )
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--campaign-id", required=True, help="Campaign ID from Poplar")
    parser.add_argument("--creative-id", help="Creative ID (optional)")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="Delay between requests in seconds (default: 0.1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without sending")
    parser.add_argument("--max", type=int, dest="max_records",
                        help="Maximum records to process")
    parser.add_argument("--error-log", help="Write errors to JSON file")

    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"Error: CSV file not found: {args.csv}", file=sys.stderr)
        sys.exit(1)

    print(f"Starting batch send from {args.csv}")
    print(f"Campaign ID: {args.campaign_id}")
    if args.creative_id:
        print(f"Creative ID: {args.creative_id}")
    if args.dry_run:
        print("MODE: Dry run (no mailings will be sent)")
    print("-" * 50)

    start_time = datetime.now()

    try:
        success, errors_count, errors = send_batch(
            csv_path=args.csv,
            campaign_id=args.campaign_id,
            creative_id=args.creative_id,
            delay=args.delay,
            dry_run=args.dry_run,
            max_records=args.max_records
        )

        duration = datetime.now() - start_time

        print("-" * 50)
        print(f"Completed in {duration.total_seconds():.1f} seconds")
        print(f"  Successful: {success}")
        print(f"  Errors: {errors_count}")

        if errors and args.error_log:
            with open(args.error_log, 'w') as f:
                json.dump(errors, f, indent=2)
            print(f"  Error log: {args.error_log}")

        if errors_count > 0:
            sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()

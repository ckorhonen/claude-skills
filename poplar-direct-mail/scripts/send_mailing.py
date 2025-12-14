#!/usr/bin/env python3
"""Send a single direct mail piece via Poplar API.

Usage:
    python send_mailing.py --campaign-id CAMPAIGN_ID --first-name John --last-name Doe \
        --address "123 Main St" --city "San Francisco" --state CA --zip 94102

Environment:
    POPLAR_API_TOKEN: Your Poplar API token (test or production)
"""

import os
import sys
import json
import argparse
import requests

POPLAR_API_URL = "https://api.heypoplar.com/v1"


def send_mailing(
    campaign_id: str,
    recipient: dict,
    creative_id: str = None,
    merge_tags: dict = None,
    send_at: str = None
) -> dict:
    """Send a mailing via Poplar API.

    Args:
        campaign_id: The campaign ID from Poplar
        recipient: Dictionary with recipient address info
        creative_id: Optional creative ID (uses campaign default if not specified)
        merge_tags: Optional dictionary of merge tags for personalization
        send_at: Optional ISO8601 datetime for scheduled sending

    Returns:
        API response dictionary with mailing details

    Raises:
        ValueError: If POPLAR_API_TOKEN is not set
        requests.exceptions.RequestException: If API request fails
    """
    token = os.environ.get("POPLAR_API_TOKEN")
    if not token:
        raise ValueError("POPLAR_API_TOKEN environment variable not set")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "campaign_id": campaign_id,
        "recipient": recipient
    }

    if creative_id:
        payload["creative_id"] = creative_id
    if merge_tags:
        payload["merge_tags"] = merge_tags
    if send_at:
        payload["send_at"] = send_at

    response = requests.post(
        f"{POPLAR_API_URL}/mailing",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Send a Poplar direct mail piece",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic mailing
    python send_mailing.py --campaign-id abc123 --first-name Jane --last-name Smith \\
        --address "456 Oak Ave" --city "Austin" --state TX --zip 78701

    # With promo code
    python send_mailing.py --campaign-id abc123 --first-name Jane --last-name Smith \\
        --address "456 Oak Ave" --city "Austin" --state TX --zip 78701 \\
        --promo-code SAVE20

    # Scheduled for future date
    python send_mailing.py --campaign-id abc123 --first-name Jane --last-name Smith \\
        --address "456 Oak Ave" --city "Austin" --state TX --zip 78701 \\
        --send-at "2024-02-01T09:00:00Z"
        """
    )
    parser.add_argument("--campaign-id", required=True, help="Campaign ID from Poplar")
    parser.add_argument("--creative-id", help="Creative ID (optional, uses campaign default)")
    parser.add_argument("--first-name", help="Recipient first name")
    parser.add_argument("--last-name", help="Recipient last name")
    parser.add_argument("--full-name", help="Recipient full name (alternative to first/last)")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--address", required=True, help="Street address (address_1)")
    parser.add_argument("--address2", help="Apartment/Suite (address_2)")
    parser.add_argument("--city", required=True, help="City")
    parser.add_argument("--state", required=True, help="State (2-letter code)")
    parser.add_argument("--zip", required=True, help="ZIP/Postal code")
    parser.add_argument("--promo-code", help="Promo code for merge tag")
    parser.add_argument("--merge-tags", help="Additional merge tags as JSON string")
    parser.add_argument("--send-at", help="Schedule for future (ISO8601 datetime)")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")

    args = parser.parse_args()

    # Build recipient object
    recipient = {
        "address_1": args.address,
        "city": args.city,
        "state": args.state,
        "postal_code": args.zip
    }

    if args.full_name:
        recipient["full_name"] = args.full_name
    else:
        if args.first_name:
            recipient["first_name"] = args.first_name
        if args.last_name:
            recipient["last_name"] = args.last_name

    if args.address2:
        recipient["address_2"] = args.address2
    if args.company:
        recipient["company"] = args.company

    # Build merge tags
    merge_tags = {}
    if args.promo_code:
        merge_tags["promo_code"] = args.promo_code
    if args.merge_tags:
        try:
            additional_tags = json.loads(args.merge_tags)
            merge_tags.update(additional_tags)
        except json.JSONDecodeError as e:
            print(f"Error parsing --merge-tags JSON: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        result = send_mailing(
            campaign_id=args.campaign_id,
            recipient=recipient,
            creative_id=args.creative_id,
            merge_tags=merge_tags if merge_tags else None,
            send_at=args.send_at
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Mailing created successfully!")
            print(f"  ID: {result['id']}")
            print(f"  Status: {result['state']}")
            print(f"  Cost: ${result.get('total_cost', 'N/A')}")
            if result.get('pdf_url'):
                print(f"  PDF Preview: {result['pdf_url']}")
            if result.get('front_url'):
                print(f"  Front Preview: {result['front_url']}")
            if result.get('back_url'):
                print(f"  Back Preview: {result['back_url']}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Details: {json.dumps(error_detail, indent=2)}", file=sys.stderr)
            except json.JSONDecodeError:
                print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

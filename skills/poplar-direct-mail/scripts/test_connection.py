#!/usr/bin/env python3
"""Test Poplar API connection and list available campaigns/creatives.

Usage:
    python test_connection.py
    python test_connection.py --campaign-id CAMPAIGN_ID

Environment:
    POPLAR_API_TOKEN: Your Poplar API token
"""

import os
import sys
import json
import argparse
import requests

POPLAR_API_URL = "https://api.heypoplar.com/v1"


def test_connection(campaign_id: str = None, json_output: bool = False) -> bool:
    """Test API connection and list available resources.

    Args:
        campaign_id: Optional campaign ID to show creatives for
        json_output: If True, output raw JSON responses

    Returns:
        True if connection successful, False otherwise
    """
    results = {"success": False, "organization": None, "campaigns": [], "creatives": []}
    token = os.environ.get("POPLAR_API_TOKEN")
    if not token:
        if json_output:
            print(json.dumps({"error": "POPLAR_API_TOKEN environment variable not set"}))
        else:
            print("Error: POPLAR_API_TOKEN environment variable not set")
            print("\nTo set your token:")
            print("  export POPLAR_API_TOKEN='your_token_here'")
            print("\nGet your token from: https://app.heypoplar.com/credentials")
        return False

    # Determine token type
    is_test = token.startswith("test")
    results["token_type"] = "test" if is_test else "production"

    if not json_output:
        print(f"Token type: {'Test' if is_test else 'Production'}")
        if is_test:
            print("  Note: Test tokens only work with the /mailing endpoint")
        print()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Test authentication
    if not json_output:
        print("Testing API connection...")
    try:
        response = requests.get(
            f"{POPLAR_API_URL}/me",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        try:
            org = response.json()
        except json.JSONDecodeError:
            org = {}
        results["organization"] = org
        if not json_output:
            print(f"  Connected to: {org.get('name', 'Unknown Organization')}")
            print(f"  Org ID: {org.get('id', 'N/A')}")
    except requests.exceptions.HTTPError as e:
        if not json_output:
            if e.response is not None and e.response.status_code == 401:
                print("  Authentication failed: Invalid token")
            elif e.response is not None and e.response.status_code == 403:
                print("  Access denied: Check token permissions")
                if is_test:
                    print("  Note: Test tokens cannot access /me endpoint")
            else:
                print(f"  Error: {e}")
        if json_output:
            print(json.dumps({"error": str(e), "results": results}))
        return False
    except requests.exceptions.RequestException as e:
        if not json_output:
            print(f"  Connection error: {e}")
        else:
            print(json.dumps({"error": str(e), "results": results}))
        return False

    if not json_output:
        print()

    # List campaigns
    if not json_output:
        print("Available campaigns:")
    try:
        response = requests.get(
            f"{POPLAR_API_URL}/campaigns",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        try:
            campaigns = response.json()
        except json.JSONDecodeError:
            campaigns = []
        results["campaigns"] = campaigns

        if not json_output:
            if not campaigns:
                print("  No campaigns found")
                print("  Create a campaign at: https://app.heypoplar.com")
            else:
                for campaign in campaigns:
                    status = "ACTIVE" if campaign.get("active") else "inactive"
                    print(f"  [{status}] {campaign.get('name', 'Unnamed')}")
                    print(f"         ID: {campaign.get('id')}")

    except requests.exceptions.HTTPError as e:
        if not json_output:
            if is_test:
                print("  Cannot list campaigns with test token")
            else:
                print(f"  Error listing campaigns: {e}")
    except requests.exceptions.RequestException as e:
        if not json_output:
            print(f"  Error: {e}")

    # Show creatives for specific campaign
    if campaign_id:
        if not json_output:
            print()
            print(f"Creatives for campaign {campaign_id}:")
        try:
            response = requests.get(
                f"{POPLAR_API_URL}/campaign/{campaign_id}/creatives",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            try:
                creatives = response.json()
            except json.JSONDecodeError:
                creatives = []
            results["creatives"] = creatives

            if not json_output:
                if not creatives:
                    print("  No creatives found")
                else:
                    for creative in creatives:
                        status = "ACTIVE" if creative.get("active") else "inactive"
                        print(f"  [{status}] {creative.get('name', 'Unnamed')}")
                        print(f"         ID: {creative.get('id')}")
                        print(f"         Format: {creative.get('format', 'N/A')}")

        except requests.exceptions.HTTPError as e:
            if not json_output:
                print(f"  Error: {e}")
        except requests.exceptions.RequestException as e:
            if not json_output:
                print(f"  Error: {e}")

    results["success"] = True
    if json_output:
        print(json.dumps(results, indent=2))
    else:
        print()
        print("Connection test complete!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test Poplar API connection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test connection and list campaigns
    python test_connection.py

    # Also show creatives for a specific campaign
    python test_connection.py --campaign-id abc123

Setup:
    1. Get your API token from https://app.heypoplar.com/credentials
    2. Set the environment variable:
       export POPLAR_API_TOKEN='your_token_here'
    3. Run this script to verify connectivity
        """
    )
    parser.add_argument("--campaign-id", help="Campaign ID to show creatives for")
    parser.add_argument("--json", action="store_true", help="Output raw JSON responses")

    args = parser.parse_args()

    success = test_connection(campaign_id=args.campaign_id, json_output=args.json)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

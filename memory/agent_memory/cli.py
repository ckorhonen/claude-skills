"""CLI for agent_memory package."""

import json
import sys
from pathlib import Path
import click
from agent_memory.knowledge import search_learnings, save_learning
from agent_memory.transcript import (
    parse_transcript,
    extract_last_assistant_message,
    extract_proposed_learning,
)


PENDING_FILE_PATH = Path.home() / ".agent_memory_pending.json"


@click.group()
def cli():
    """Agent Memory CLI - Store and retrieve agent learnings."""
    pass


@cli.command()
@click.option('--query', required=True, help='Search query')
@click.option('--max-results', default=5, type=int, help='Maximum number of results')
def search(query: str, max_results: int):
    """Search for learnings."""
    try:
        results = search_learnings(query, max_results)

        if not results:
            click.echo("No results found.")
            return

        click.echo(f"Found {len(results)} result(s):\n")
        for i, result in enumerate(results, 1):
            click.echo(f"--- Result {i} ---")
            click.echo(f"Title: {result.get('title', 'N/A')}")
            click.echo(f"Type: {result.get('type', 'N/A')}")
            click.echo(f"Confidence: {result.get('confidence', 'N/A')}")
            click.echo(f"Learning: {result.get('learning', 'N/A')}")
            click.echo(f"Context: {result.get('context', 'N/A')}")
            click.echo(f"Repo: {result.get('repo', 'N/A')}")
            click.echo(f"Tags: {', '.join(result.get('tags', []))}")
            click.echo(f"Created: {result.get('created_at', 'N/A')}")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--pending-file', type=click.Path(exists=True), help='Path to pending learning file')
@click.option('--payload-json', help='JSON string of learning payload')
def save(pending_file: str | None, payload_json: str | None):
    """Save a learning to the database."""
    if not pending_file and not payload_json:
        click.echo("Error: Must provide either --pending-file or --payload-json", err=True)
        sys.exit(1)

    if pending_file and payload_json:
        click.echo("Error: Provide only one of --pending-file or --payload-json", err=True)
        sys.exit(1)

    try:
        if pending_file:
            with open(pending_file, 'r') as f:
                payload = json.load(f)
        else:
            payload = json.loads(payload_json)

        # Validate required fields
        required_fields = ['title', 'context', 'learning', 'confidence', 'type', 'created_at', 'repo']
        missing_fields = [field for field in required_fields if field not in payload]

        if missing_fields:
            click.echo(f"Error: Missing required fields: {', '.join(missing_fields)}", err=True)
            sys.exit(1)

        # Validate enum fields
        valid_confidence = ['low', 'medium', 'high']
        valid_types = ['rule', 'heuristic', 'source', 'process', 'constraint']

        if payload['confidence'] not in valid_confidence:
            click.echo(f"Error: confidence must be one of: {', '.join(valid_confidence)}", err=True)
            sys.exit(1)

        if payload['type'] not in valid_types:
            click.echo(f"Error: type must be one of: {', '.join(valid_types)}", err=True)
            sys.exit(1)

        save_learning(payload)
        click.echo("Learning saved successfully!")

        # If we used a pending file, optionally remove it
        if pending_file:
            click.echo(f"You can now delete {pending_file}")

    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def pending():
    """Manage pending learnings."""
    pass


@pending.command(name='show')
def pending_show():
    """Show pending learning."""
    if not PENDING_FILE_PATH.exists():
        click.echo("No pending learning found.")
        return

    try:
        with open(PENDING_FILE_PATH, 'r') as f:
            payload = json.load(f)

        click.echo("Pending learning:")
        click.echo(json.dumps(payload, indent=2))
    except Exception as e:
        click.echo(f"Error reading pending file: {e}", err=True)
        sys.exit(1)


@pending.command(name='clear')
def pending_clear():
    """Clear pending learning."""
    if PENDING_FILE_PATH.exists():
        PENDING_FILE_PATH.unlink()
        click.echo("Pending learning cleared.")
    else:
        click.echo("No pending learning to clear.")


@pending.command(name='save')
def pending_save():
    """Save the pending learning to the database."""
    if not PENDING_FILE_PATH.exists():
        click.echo("No pending learning found.", err=True)
        sys.exit(1)

    try:
        with open(PENDING_FILE_PATH, 'r') as f:
            payload = json.load(f)

        save_learning(payload)
        click.echo("Pending learning saved successfully!")

        # Clear the pending file
        PENDING_FILE_PATH.unlink()
        click.echo("Pending file cleared.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

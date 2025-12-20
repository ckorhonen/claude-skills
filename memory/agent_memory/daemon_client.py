#!/usr/bin/env python3
"""
Memory daemon client - thin socket client for hooks.

Fast-failing client (500ms timeout) for communicating with the memory daemon.
Falls back gracefully if daemon is unavailable.

Socket: ~/.claude/daemon.sock
"""

import json
import os
import socket
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Socket configuration
SOCKET_PATH = Path.home() / ".claude" / "daemon.sock"
PID_FILE = Path.home() / ".claude" / "daemon.pid"
SOCKET_TIMEOUT = 0.5  # 500ms timeout for fast fail


class DaemonClient:
    """Client for communicating with memory daemon via Unix socket."""

    def __init__(self, socket_path: Path = SOCKET_PATH, timeout: float = SOCKET_TIMEOUT):
        self.socket_path = socket_path
        self.timeout = timeout
        self.sock = None

    def connect(self) -> bool:
        """Connect to daemon socket."""
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect(str(self.socket_path))
            return True
        except (FileNotFoundError, ConnectionRefusedError, socket.timeout):
            return False
        except Exception:
            return False

    def close(self):
        """Close socket connection."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def send_request(self, method: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Send request to daemon and receive response.

        Args:
            method: Method name to call
            params: Optional parameters dict

        Returns:
            Response dict, or None if daemon unavailable
        """
        if not self.connect():
            return None

        try:
            request = {
                'method': method,
                'params': params or {}
            }

            # Send request
            data = json.dumps(request).encode('utf-8')
            self.sock.sendall(data)

            # Receive response
            response_data = self.sock.recv(65536)
            if not response_data:
                return None

            response = json.loads(response_data.decode('utf-8'))
            return response

        except (socket.timeout, ConnectionError, BrokenPipeError):
            return None
        except json.JSONDecodeError:
            return None
        except Exception:
            return None
        finally:
            self.close()

    def ping(self) -> bool:
        """
        Ping daemon to check if it's alive.

        Returns:
            True if daemon is responsive, False otherwise
        """
        response = self.send_request('ping')
        return response is not None and response.get('status') == 'ok'

    def search_learnings(self, cwd: str, query: Optional[str] = None,
                        limit: int = 10, scope_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search learnings across scopes.

        Args:
            cwd: Current working directory
            query: Optional search query
            limit: Maximum results to return
            scope_filter: Optional scope filter ('global', 'organization', 'repository', 'directory')

        Returns:
            List of learning dicts, or empty list if daemon unavailable
        """
        response = self.send_request('search_learnings', {
            'cwd': cwd,
            'query': query,
            'limit': limit,
            'scope_filter': scope_filter
        })

        if response and 'results' in response:
            return response['results']
        return []

    def save_learning(self, repo_identifier: Optional[str], title: str, content: str,
                     category: Optional[str] = None, tags: Optional[List[str]] = None,
                     session_id: Optional[str] = None, metadata: Optional[Dict] = None,
                     scope_level: str = "repository", directory_path: Optional[str] = None) -> Optional[int]:
        """
        Save a learning to the database.

        Args:
            repo_identifier: Repository identifier
            title: Learning title
            content: Learning content
            category: Optional category
            tags: Optional tags list
            session_id: Optional session ID
            metadata: Optional metadata dict
            scope_level: Scope level ('global', 'organization', 'repository', 'directory')
            directory_path: Optional directory path for directory scope

        Returns:
            Learning ID if successful, None otherwise
        """
        response = self.send_request('save_learning', {
            'repo_identifier': repo_identifier,
            'title': title,
            'content': content,
            'category': category,
            'tags': tags,
            'session_id': session_id,
            'metadata': metadata,
            'scope_level': scope_level,
            'directory_path': directory_path
        })

        if response and 'id' in response:
            return response['id']
        return None

    def get_repo_identifier(self, cwd: str) -> Optional[str]:
        """
        Get repository identifier for a directory.

        Args:
            cwd: Current working directory

        Returns:
            Repository identifier, or None if daemon unavailable
        """
        response = self.send_request('get_repo_identifier', {'cwd': cwd})

        if response and 'repo_id' in response:
            return response['repo_id']
        return None

    def queue_extraction(self, transcript_data: Dict, cwd: str) -> bool:
        """
        Queue transcript for background LLM extraction.

        Args:
            transcript_data: Transcript data dict
            cwd: Current working directory

        Returns:
            True if successfully queued, False otherwise
        """
        response = self.send_request('queue_extraction', {
            'transcript_data': transcript_data,
            'cwd': cwd
        })

        return response is not None and response.get('status') == 'queued'

    def init_db(self) -> bool:
        """
        Initialize database schema.

        Returns:
            True if successful, False otherwise
        """
        response = self.send_request('init_db')
        return response is not None and response.get('success') is True


# Helper functions for easy usage


def is_daemon_running() -> bool:
    """
    Check if daemon is running.

    Returns:
        True if daemon is running and responsive
    """
    # Check if PID file exists
    if not PID_FILE.exists():
        return False

    # Try to ping daemon
    client = DaemonClient()
    return client.ping()


def get_client() -> DaemonClient:
    """
    Get a daemon client instance.

    Returns:
        DaemonClient instance
    """
    return DaemonClient()


def start_daemon() -> bool:
    """
    Start the daemon if not already running.

    Returns:
        True if daemon is running after this call
    """
    if is_daemon_running():
        return True

    try:
        import subprocess
        import sys

        # Get path to daemon.py
        daemon_path = Path(__file__).parent / "daemon.py"

        # Start daemon in background
        subprocess.Popen(
            [sys.executable, str(daemon_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        # Wait up to 2 seconds for daemon to start
        for _ in range(20):
            time.sleep(0.1)
            if is_daemon_running():
                return True

        return False

    except Exception:
        return False


def stop_daemon() -> bool:
    """
    Stop the daemon if running.

    Returns:
        True if daemon stopped successfully
    """
    if not PID_FILE.exists():
        return True

    try:
        import signal

        pid = int(PID_FILE.read_text())

        # Send SIGTERM
        os.kill(pid, signal.SIGTERM)

        # Wait up to 5 seconds for daemon to stop
        for _ in range(50):
            time.sleep(0.1)
            if not is_daemon_running():
                return True

        # Force kill if still running
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

        return True

    except (ValueError, ProcessLookupError):
        # PID file corrupt or process already dead
        if PID_FILE.exists():
            PID_FILE.unlink()
        return True
    except Exception:
        return False


# Convenience functions that auto-handle client lifecycle


def ping() -> bool:
    """Ping the daemon."""
    client = get_client()
    return client.ping()


def search_learnings(cwd: str, query: Optional[str] = None,
                    limit: int = 10, scope_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search learnings via daemon."""
    client = get_client()
    return client.search_learnings(cwd, query, limit, scope_filter)


def save_learning(repo_identifier: Optional[str], title: str, content: str,
                 category: Optional[str] = None, tags: Optional[List[str]] = None,
                 session_id: Optional[str] = None, metadata: Optional[Dict] = None,
                 scope_level: str = "repository", directory_path: Optional[str] = None) -> Optional[int]:
    """Save a learning via daemon."""
    client = get_client()
    return client.save_learning(repo_identifier, title, content, category, tags,
                                session_id, metadata, scope_level, directory_path)


def get_repo_identifier(cwd: str) -> Optional[str]:
    """Get repository identifier via daemon."""
    client = get_client()
    return client.get_repo_identifier(cwd)


def queue_extraction(transcript_data: Dict, cwd: str) -> bool:
    """Queue extraction via daemon."""
    client = get_client()
    return client.queue_extraction(transcript_data, cwd)


def init_db() -> bool:
    """Initialize database via daemon."""
    client = get_client()
    return client.init_db()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "start":
            if start_daemon():
                print("Daemon started successfully")
                sys.exit(0)
            else:
                print("Failed to start daemon", file=sys.stderr)
                sys.exit(1)

        elif command == "stop":
            if stop_daemon():
                print("Daemon stopped successfully")
                sys.exit(0)
            else:
                print("Failed to stop daemon", file=sys.stderr)
                sys.exit(1)

        elif command == "status":
            if is_daemon_running():
                print("Daemon is running")
                sys.exit(0)
            else:
                print("Daemon is not running")
                sys.exit(1)

        elif command == "ping":
            if ping():
                print("Daemon is responsive")
                sys.exit(0)
            else:
                print("Daemon is not responsive")
                sys.exit(1)

        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            print("Usage: daemon_client.py [start|stop|status|ping]", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: daemon_client.py [start|stop|status|ping]", file=sys.stderr)
        sys.exit(1)

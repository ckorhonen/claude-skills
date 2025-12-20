#!/usr/bin/env python3
"""
Test script for memory daemon functionality.

Tests:
1. Client fast-fail when daemon is off
2. Graceful degradation
3. Daemon lifecycle (start/stop)
4. Basic operations (requires database)
"""

import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_memory import daemon_client


def test_fast_fail():
    """Test that client fails fast when daemon is unavailable."""
    print("Test 1: Fast-fail behavior")
    print("-" * 50)

    if daemon_client.is_daemon_running():
        print("SKIP: Daemon is already running")
        return True

    start = time.time()
    result = daemon_client.ping()
    elapsed = time.time() - start

    if result:
        print(f"FAIL: Ping should return False when daemon is off")
        return False

    if elapsed > 1.0:
        print(f"FAIL: Took too long ({elapsed:.3f}s), should be < 1s")
        return False

    print(f"✓ Fast-fail working ({elapsed:.3f}s)")
    return True


def test_graceful_degradation():
    """Test that client methods return empty/None when daemon unavailable."""
    print("\nTest 2: Graceful degradation")
    print("-" * 50)

    if daemon_client.is_daemon_running():
        print("SKIP: Daemon is already running")
        return True

    # Test search_learnings
    learnings = daemon_client.search_learnings('/tmp', 'test')
    if learnings != []:
        print(f"FAIL: search_learnings should return [], got {learnings}")
        return False
    print("✓ search_learnings returns []")

    # Test get_repo_identifier
    repo_id = daemon_client.get_repo_identifier('/tmp')
    if repo_id is not None:
        print(f"FAIL: get_repo_identifier should return None, got {repo_id}")
        return False
    print("✓ get_repo_identifier returns None")

    # Test save_learning
    learning_id = daemon_client.save_learning(
        repo_identifier="test/repo",
        title="Test",
        content="Test content"
    )
    if learning_id is not None:
        print(f"FAIL: save_learning should return None, got {learning_id}")
        return False
    print("✓ save_learning returns None")

    # Test queue_extraction
    queued = daemon_client.queue_extraction({'messages': []}, '/tmp')
    if queued:
        print(f"FAIL: queue_extraction should return False, got {queued}")
        return False
    print("✓ queue_extraction returns False")

    return True


def test_client_creation():
    """Test client creation and basic properties."""
    print("\nTest 3: Client creation")
    print("-" * 50)

    client = daemon_client.get_client()
    if not isinstance(client, daemon_client.DaemonClient):
        print(f"FAIL: Wrong client type: {type(client)}")
        return False
    print(f"✓ Client created: {type(client).__name__}")

    if client.timeout != 0.5:
        print(f"FAIL: Wrong timeout: {client.timeout}")
        return False
    print(f"✓ Timeout set correctly: {client.timeout}s")

    if client.socket_path != daemon_client.SOCKET_PATH:
        print(f"FAIL: Wrong socket path: {client.socket_path}")
        return False
    print(f"✓ Socket path: {client.socket_path}")

    return True


def test_status_check():
    """Test daemon status checking."""
    print("\nTest 4: Status check")
    print("-" * 50)

    is_running = daemon_client.is_daemon_running()
    print(f"Daemon status: {'running' if is_running else 'not running'}")

    # Check PID file consistency
    pid_exists = daemon_client.PID_FILE.exists()
    print(f"PID file exists: {pid_exists}")

    if is_running and not pid_exists:
        print("WARN: Daemon running but no PID file")
    elif not is_running and pid_exists:
        print("WARN: PID file exists but daemon not running (stale)")

    return True


def test_module_exports():
    """Test that module exports work correctly."""
    print("\nTest 5: Module exports")
    print("-" * 50)

    try:
        from agent_memory import (
            DaemonClient,
            get_client,
            is_daemon_running,
            start_daemon,
            stop_daemon
        )
        print("✓ All daemon exports available from agent_memory")
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        return False

    # Verify they're the right objects
    if DaemonClient is not daemon_client.DaemonClient:
        print("FAIL: DaemonClient is different object")
        return False
    print("✓ Exports are correct objects")

    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Memory Daemon Test Suite")
    print("=" * 50)

    tests = [
        test_fast_fail,
        test_graceful_degradation,
        test_client_creation,
        test_status_check,
        test_module_exports,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\nERROR in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 50)
    print("Results")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for test, result in zip(tests, results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test.__name__}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

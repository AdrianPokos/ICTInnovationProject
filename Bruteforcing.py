"""
Brute-force protection

This is a self-contained CLI simulator of the same defensive logic:
- per-IP counters
- per-username failures and temporary lockout
- exponential backoff
- admin/status view

No external dependencies. Run with the Python interpreter in a virtualenv:
    python bruteforce_simulator.py --help
"""

import time
import argparse
import random
import sys

# --- Configuration (same semantics as before) ---
IP_MAX_ATTEMPTS = 30
IP_WINDOW_SECONDS = 60 * 5    # 5 minutes
USER_MAX_ATTEMPTS = 5
USER_LOCK_SECONDS = 60 * 15   # 15 minutes
BACKOFF_BASE = 1.5
MAX_BACKOFF_SECONDS = 8

# --- In-process memory store (no Redis) ---
class MemoryStore:
    def __init__(self):
        # key -> (int_value, expire_ts_or_None)
        self._data = {}
    def _purge_expired(self):
        now = time.time()
        to_delete = [k for k,(v,exp) in self._data.items() if exp is not None and exp <= now]
        for k in to_delete:
            del self._data[k]
    def incr(self, key, expiration=None):
        self._purge_expired()
        now = time.time()
        v, exp = self._data.get(key, (0, None))
        v += 1
        new_exp = (now + expiration) if expiration is not None else None
        self._data[key] = (v, new_exp)
        return v
    def get(self, key):
        self._purge_expired()
        v, _ = self._data.get(key, (None, None))
        return v
    def set(self, key, value, expiration=None):
        self._purge_expired()
        new_exp = (time.time() + expiration) if expiration is not None else None
        self._data[key] = (int(value), new_exp)
    def delete(self, key):
        self._data.pop(key, None)

# Single global store instance
store = MemoryStore()

# Helper key functions
def ip_key(ip): return f"ip:{ip}"
def user_failure_key(username): return f"user_fail:{username}"
def user_lock_key(username): return f"user_lock:{username}"
def user_backoff_key(username): return f"user_backoff:{username}"

# Utils
def is_ip_blocked(ip):
    count = store.get(ip_key(ip)) or 0
    return count >= IP_MAX_ATTEMPTS

def is_user_locked(username):
    return bool(store.get(user_lock_key(username)))

def record_failed_attempt(ip, username):
    ip_count = store.incr(ip_key(ip), expiration=IP_WINDOW_SECONDS)
    user_failures = store.incr(user_failure_key(username), expiration=USER_LOCK_SECONDS)
    return ip_count, user_failures

def lock_user(username):
    store.set(user_lock_key(username), 1, expiration=USER_LOCK_SECONDS)

def apply_backoff(username):
    backoff = store.get(user_backoff_key(username)) or 0
    if backoff <= 0:
        backoff = 1
    else:
        backoff = min(int(backoff * BACKOFF_BASE), MAX_BACKOFF_SECONDS)
    store.set(user_backoff_key(username), backoff, expiration=IP_WINDOW_SECONDS)
    # Simulate server-side delay (for demo we print before sleeping)
    print(f"  [server] applying backoff {backoff}s for user={username}")
    time.sleep(backoff)

def reset_user_state(username):
    store.delete(user_failure_key(username))
    store.delete(user_backoff_key(username))

def get_status(username):
    locked = bool(store.get(user_lock_key(username)))
    failures = store.get(user_failure_key(username)) or 0
    backoff = store.get(user_backoff_key(username)) or 0
    return {"username": username, "locked": locked, "failures": failures, "backoff": backoff}

# Demo auth check (replace as needed)
DUMMY_DB = {"alice": "s3cret", "bob": "hunter2"}

def verify_credentials(username, password):
    return DUMMY_DB.get(username) == password

# Core login simulation (returns status_code, message)
def simulate_login_attempt(ip, username, password, do_backoff=True):
    username = (username or "").lower().strip()
    if not username:
        return 400, "missing username"

    if is_ip_blocked(ip):
        return 429, "too many requests from this IP, try later"

    if is_user_locked(username):
        return 423, "account temporarily locked"

    # Optional server-side backoff (non-blocking simulation in CLI we will sleep)
    backoff_value = store.get(user_backoff_key(username)) or 0
    if backoff_value and do_backoff:
        print(f"  [server] current backoff {backoff_value}s for user={username}")
        time.sleep(min(int(backoff_value), MAX_BACKOFF_SECONDS))

    ok = verify_credentials(username, password)
    if ok:
        reset_user_state(username)
        return 200, "logged in"

    # failed login
    ip_count, user_failures = record_failed_attempt(ip, username)

    if user_failures >= USER_MAX_ATTEMPTS:
        lock_user(username)
        return 423, "account temporarily locked due to repeated failed logins"

    if ip_count >= IP_MAX_ATTEMPTS // 2:
        # In a real app you'd require CAPTCHA or similar
        pass

    if do_backoff:
        apply_backoff(username)

    return 401, "invalid credentials"

# CLI helpers
def run_demo_sequence(target_username="alice", passwords=None, ips=None, rounds=1, delay=0.5):
    """
    Simulate password attempts from a small set of IPs.
    - passwords: list of passwords to try
    - ips: list of IP strings to simulate (round-robin)
    """
    if passwords is None:
        passwords = ["wrong1", "wrong2", "wrong3", "wrong4", "wrong5", "s3cret"]
    if ips is None:
        ips = ["10.0.0.1"]  # default single IP

    attempt = 0
    for r in range(rounds):
        print(f"\n--- Round {r+1}/{rounds} ---")
        for pwd in passwords:
            attempt += 1
            ip = random.choice(ips)
            print(f"Attempt #{attempt} from ip={ip} username={target_username} password='{pwd}' ...", end=" ")
            code, msg = simulate_login_attempt(ip, target_username, pwd)
            print(f"-> {code} {msg}")
            if code == 423 or (isinstance(msg, str) and "too many" in msg):
                print("  [demo] server indicates lockout/rate-limit. Stopping further attempts.")
                return
            time.sleep(delay)
    print("\nDemo sequence finished.\n")

def interactive_mode():
    print("Interactive mode. Type 'exit' to quit, 'status <user>' to view user status.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return
        if not line:
            continue
        if line.lower() in ("exit","quit"):
            print("Exiting.")
            return
        if line.startswith("status "):
            _, user = line.split(None, 1)
            print(get_status(user))
            continue
        parts = line.split()
        if len(parts) < 3:
            print("Usage: <ip> <username> <password>   OR  status <username>")
            continue
        ip, user, pwd = parts[0], parts[1], " ".join(parts[2:])
        code, msg = simulate_login_attempt(ip, user, pwd)
        print(f"-> {code} {msg}")

def main():
    parser = argparse.ArgumentParser(description="Brute-force protection simulator (no Flask/no Redis).")
    parser.add_argument("--demo", action="store_true", help="Run a demo sequence (pre-configured attempts).")
    parser.add_argument("--username", type=str, default="alice", help="Target username for demo/attempts.")
    parser.add_argument("--rounds", type=int, default=2, help="Number of rounds when running demo.")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between demo attempts.")
    parser.add_argument("--ips", type=str, default="10.0.0.1", help="Comma-separated list of IPs for demo (e.g. '1.2.3.4,5.6.7.8').")
    parser.add_argument("--passwords", type=str, default=None, help="Comma-separated passwords list to try (default includes correct).")
    parser.add_argument("--interactive", action="store_true", help="Run interactive prompt to perform single attempts manually.")
    args = parser.parse_args()

    if args.demo:
        pwds = args.passwords.split(",") if args.passwords else None
        ips = [p.strip() for p in args.ips.split(",") if p.strip()]
        run_demo_sequence(target_username=args.username, passwords=pwds, ips=ips, rounds=args.rounds, delay=args.delay)
        return

    if args.interactive:
        interactive_mode()
        return

    print("No mode selected. Use --demo or --interactive. See --help for options.")

if __name__ == "__main__":
    main()

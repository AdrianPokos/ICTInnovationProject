"""
Demo tester for brutefoce

What it does:
- Sends a sequence of login attempts to the target URL (default: http://127.0.0.1:5000/login)
- Prints status codes and JSON responses
- Can simulate repeated failures to demonstrate lockouts and backoff
- Respects a small delay between attempts by default to avoid accidental DoS

Usage:
    pip install requests
    python demo_bruteforce_test.py

"""

import time
import requests

# Config
TARGET_URL = "http://127.0.0.1:5000/login"  # your local Flask endpoint
USERNAME = "alice"
# A list of passwords to try. The demo will iterate this list.
# Include deliberately-wrong passwords to trigger the defensive logic.
PASSWORDS = ["wrong1", "wrong2", "wrong3", "wrong4", "wrong5", "s3cret"]
NUM_ROUNDS = 2          # how many times to cycle through the PASSWORDS list
DELAY_BETWEEN_REQUESTS = 0.5  # seconds between requests (keep this modest)
PRINT_EACH = True

# Safety check
print("Demo brute-force tester (AUTHORIZED LOCAL TESTS ONLY)")
print("Target:", TARGET_URL)
print("Username:", USERNAME)
print("Rounds:", NUM_ROUNDS, "Passwords per round:", len(PASSWORDS))
print("Delay between requests:", DELAY_BETWEEN_REQUESTS, "s")
print("---")
print("Starting in 3 seconds. Press Ctrl+C to abort.")
try:
    time.sleep(3)
except KeyboardInterrupt:
    print("Aborted by user")
    raise SystemExit

session = requests.Session()

attempt = 0
for r in range(NUM_ROUNDS):
    print(f"\n--- Round {r+1}/{NUM_ROUNDS} ---")
    for pwd in PASSWORDS:
        attempt += 1
        payload = {"username": USERNAME, "password": pwd}
        try:
            resp = session.post(TARGET_URL, json=payload, timeout=5)
            text = ""
            try:
                text = resp.json()
            except Exception:
                text = resp.text
            status = resp.status_code
        except requests.exceptions.RequestException as e:
            status = None
            text = str(e)

        if PRINT_EACH:
            print(f"Attempt #{attempt}: password='{pwd}' -> status={status}, response={text}")

        # If the server indicates account locked or too many requests, show and optionally stop
        if isinstance(text, dict) and (text.get("error") and ("locked" in text.get("error") or "too many" in text.get("error"))):
            print("Server indicates lockout or rate limit. Stopping further attempts.")
            raise SystemExit

        time.sleep(DELAY_BETWEEN_REQUESTS)

print("\nDone.\n")
print("Tip: adjust PASSWORDS, NUM_ROUNDS, and DELAY_BETWEEN_REQUESTS for different test patterns.")

"""
Single-file defensive brute-force protection example (Flask).
Includes:
 - MemoryStore and RedisStore implementations
 - choose_store helper that picks Redis if available/reachable
 - login endpoint with per-IP limits, per-user failures, lockout, backoff
 - admin/status endpoint to inspect counters

Run:
    pip install flask redis
    python Bruteforcing.py

If you don't have Redis installed locally, the script will automatically use the in-memory store.
"""

from flask import Flask, request, jsonify
import time
import logging

# optional Redis module detection
try:
    import redis
    REDIS_MODULE_AVAILABLE = True
except ImportError:
    REDIS_MODULE_AVAILABLE = False

# --- Configuration ---
IP_MAX_ATTEMPTS = 30
IP_WINDOW_SECONDS = 60 * 5    # 5 minutes
USER_MAX_ATTEMPTS = 5
USER_LOCK_SECONDS = 60 * 15   # 15 minutes
BACKOFF_BASE = 1.5
MAX_BACKOFF_SECONDS = 8
USE_REDIS = True              # set False to force MemoryStore
REDIS_URL = "redis://localhost:6379/0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bruteforce-protect")

app = Flask(__name__)

# --- Storage classes ---
class Store:
    def incr(self, key, expiration=None):
        raise NotImplementedError
    def get(self, key):
        raise NotImplementedError
    def set(self, key, value, expiration=None):
        raise NotImplementedError
    def delete(self, key):
        raise NotImplementedError

class MemoryStore(Store):
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

class RedisStore(Store):
    def __init__(self, url="redis://localhost:6379/0"):
        # assume 'redis' package is importable if this is called
        self.r = redis.Redis.from_url(url, decode_responses=True)
    def incr(self, key, expiration=None):
        val = self.r.incr(key)
        if expiration:
            self.r.expire(key, expiration)
        return int(val)
    def get(self, key):
        v = self.r.get(key)
        return int(v) if v is not None else None
    def set(self, key, value, expiration=None):
        self.r.set(key, int(value), ex=expiration)
    def delete(self, key):
        self.r.delete(key)

# --- choose_store helper (must come after store classes) ---
def choose_store(redis_if_available=True, redis_url=REDIS_URL):
    """
    Try to use Redis if available and reachable; otherwise return MemoryStore.
    """
    if not redis_if_available:
        logger.info("Redis disabled by config; using in-memory store")
        return MemoryStore()

    if not REDIS_MODULE_AVAILABLE:
        logger.info("redis python package not installed; using in-memory store")
        return MemoryStore()

    try:
        r = redis.Redis.from_url(redis_url, decode_responses=True)
        r.ping()
        logger.info("Connected to Redis at %s", redis_url)
        return RedisStore(url=redis_url)
    except Exception as e:
        logger.warning("Redis not reachable (%s); falling back to in-memory store", e)
        return MemoryStore()

# choose store instance
store = choose_store(redis_if_available=USE_REDIS, redis_url=REDIS_URL)

# --- Helper key functions ---
def ip_key(ip):
    return f"ip:{ip}"
def user_failure_key(username):
    return f"user_fail:{username}"
def user_lock_key(username):
    return f"user_lock:{username}"
def user_backoff_key(username):
    return f"user_backoff:{username}"

# --- Utilities ---
def get_remote_ip():
    # If behind proxy, validate X-Forwarded-For appropriately in production.
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"

def apply_backoff_delay(username):
    backoff = store.get(user_backoff_key(username)) or 0
    if backoff <= 0:
        backoff = 1
    else:
        backoff = min(int(backoff * BACKOFF_BASE), MAX_BACKOFF_SECONDS)
    store.set(user_backoff_key(username), backoff, expiration=IP_WINDOW_SECONDS)
    logger.debug("Applying backoff of %s seconds for user=%s", backoff, username)
    time.sleep(backoff)

def record_failed_attempt(ip, username):
    ip_count = store.incr(ip_key(ip), expiration=IP_WINDOW_SECONDS)
    user_failures = store.incr(user_failure_key(username), expiration=USER_LOCK_SECONDS)
    logger.info("Failed login attempt: ip=%s (count=%d), user=%s (failures=%d)", ip, ip_count, username, user_failures)
    return ip_count, user_failures

def lock_user(username):
    store.set(user_lock_key(username), 1, expiration=USER_LOCK_SECONDS)
    logger.warning("User %s locked for %d seconds", username, USER_LOCK_SECONDS)

def is_user_locked(username):
    return bool(store.get(user_lock_key(username)))

def is_ip_blocked(ip):
    c = store.get(ip_key(ip)) or 0
    return c >= IP_MAX_ATTEMPTS

def reset_user_failures(username):
    store.delete(user_failure_key(username))
    store.delete(user_backoff_key(username))

# --- Auth placeholder (replace with real secure auth) ---
def verify_credentials(username, password):
    # Demo only: substitute with secure hashed password check
    DUMMY_DB = {"alice": "s3cret"}
    return DUMMY_DB.get(username) == password

# --- Flask routes ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = (data.get("username") or "").lower().strip()
    password = data.get("password", "")
    ip = get_remote_ip()

    if not username:
        return jsonify({"error": "missing username"}), 400

    if is_ip_blocked(ip):
        logger.warning("Blocking requests from IP %s due to rate limit", ip)
        return jsonify({"error": "too many requests from this IP, try later"}), 429

    if is_user_locked(username):
        logger.warning("Attempt to login to locked account: %s from ip=%s", username, ip)
        return jsonify({"error": "account temporarily locked due to failed attempts"}), 423

    backoff = store.get(user_backoff_key(username)) or 0
    if backoff:
        logger.debug("Server-side backoff: sleeping %s for user=%s", backoff, username)
        time.sleep(min(int(backoff), MAX_BACKOFF_SECONDS))

    ok = verify_credentials(username, password)
    if ok:
        reset_user_failures(username)
        logger.info("Successful login for user=%s from ip=%s", username, ip)
        return jsonify({"ok": True, "message": "logged in"}), 200

    ip_count, user_failures = record_failed_attempt(ip, username)

    if user_failures >= USER_MAX_ATTEMPTS:
        lock_user(username)
        logger.warning("User %s reached failure threshold and was locked (from ip=%s)", username, ip)
        return jsonify({"error": "account temporarily locked due to repeated failed logins"}), 423

    if ip_count >= IP_MAX_ATTEMPTS // 2:
        logger.info("IP %s approaching rate limit: %d/%d", ip, ip_count, IP_MAX_ATTEMPTS)
        # Optionally require captcha here

    apply_backoff_delay(username)

    return jsonify({"error": "invalid credentials"}), 401

@app.route("/admin/status/<username>", methods=["GET"])
def admin_status(username):
    locked = bool(store.get(user_lock_key(username)))
    failures = store.get(user_failure_key(username)) or 0
    backoff = store.get(user_backoff_key(username)) or 0
    return jsonify({"username": username, "locked": locked, "failures": failures, "backoff": backoff})

if __name__ == "__main__":
    print("Starting Flask on 127.0.0.1:5000 (debug mode, no reloader) ...")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
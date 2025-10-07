# PSEUDOCODE (Python-style) — defensive brute-force protection

# config
IP_MAX_ATTEMPTS = 30
IP_WINDOWS_SECONDS = 300        # 5 minutes
USER_MAX_ATTEMPTS = 5
USER_LOCK_SECONDS = 900         # 15 minutes
BACKOFF_BASE = 1.5
MAX_BACKOFF_SECONDS = 8

# store: abstract counter store (use Redis in real system; memory for demo)
store = choose_store(redis_if_available=True)

# helper key builders
def ip_key(ip): return "ip:" + ip
def user_fail_key(user): return "user_fail:" + user
def user_lock_key(user): return "user_lock:" + user
def user_backoff_key(user): return "user_backoff:" + user

# utility: get client IP
def get_client_ip(request):
    if request.has_header("X-Forwarded-For"):
        return first_ip_from_header(request.header["X-Forwarded-For"])
    return request.remote_addr

# check if IP is blocked
def is_ip_blocked(ip):
    count = store.get(ip_key(ip)) or 0
    return (count >= IP_MAX_ATTEMPTS)

# check if user is locked
def is_user_locked(username):
    return store.get(user_lock_key(username)) is not None

# record a failed attempt (ip + usernsame)
def record_failed_attempt(ip, username):
    ip_count = store.incr(ip_key(ip), expiry=IP_WINDOW_SECONDS)
    user_failures = store.incr(user_fail_key(username), expiry=USER_LOCK_SECONDS)
    return ip_count, user_failures

# lock user account for a while
def lock_user(username):
    store.set(user_lock_key(username), 1, expiry=USER_LOCK_SECONDS)

# apply small server-side exponential backoff delay
def apply_backoff(username):
    backoff = store.get(user_backoff_key(username)) or 1
    new_backoff = min(int(backoff * BACKOFF_BASE), MAX_BACKOFF_SECONDS)
    store.set(user_backoff_key(username), new_backoff, expiry=IP_WINDOW_SECONDS)
    sleep(new_backoff)

# reset user's failure counters on successful login
def reset_user_state(username):
    store.delete(user_fail_key(username))
    store.delete(user_backoff_key(username))

# authentication check (placeholder)
def verify_credentials(username, password):
    # return True if credentials are valid
    # (replace with real, timing-safe password verification)
    pass

# login endpoint
def login_endpoint(request):
    ip = get_client_ip(request)
    username = sanitize_lower(request.json["username"])
    password = request.json["password"]

    if not username:
        return response(400, "missing username")

    if is_ip_blocked(ip):
        return response(429, "too many requests from this IP, try later")

    if is_user_locked(username):
        return response(423, "account temporarily locked")

    # optional: small slowdown if backoff present
    current_backoff = store.get(user_backoff_key(username))
    if current_backoff:
        sleep(min(int(current_backoff), MAX_BACKOFF_SECONDS))

    if verify_credentials(username, password):
        reset_user_state(username)
        return response(200, "logged in")

    # failed login
    ip_count, user_failures = record_failed_attempt(ip, username)

    if user_failures >= USER_MAX_ATTEMPTS:
        lock_user(username)
        log("user locked", username, ip)
        return response(423, "account temporarily locked")

    if ip_count >= IP_MAX_ATTEMPTS // 2:
        # e.g. require CAPTCHA, notify, or tighten throttling
        maybe_trigger_captcha_for_ip(ip)

    apply_backoff(username)   # slows repeated attempts for that username
    log("failed login", username, ip, ip_count, user_failures)
    return response(401, "invalid credentials")
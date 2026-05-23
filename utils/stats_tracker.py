"""
Persistent Stats Tracker — saves all module activity counts to logs/stats.json
"""

import json
import os
from datetime import datetime

_STATS_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "stats.json")
_STATS_FILE = os.path.normpath(_STATS_FILE)

_DEFAULT = {
    "passwords_cracked":       0,
    "crack_attempts":          0,
    "emails_analyzed":         0,
    "phishing_emails_detected":0,
    "phishing_emails_sent":    0,
    "passwords_analyzed":      0,
    "breaches_checked":        0,
    "last_reset":              None,
    "history": [],              # list of {time, event, detail}
}


def _load() -> dict:
    os.makedirs(os.path.dirname(_STATS_FILE), exist_ok=True)
    if os.path.exists(_STATS_FILE):
        try:
            with open(_STATS_FILE, "r") as f:
                data = json.load(f)
            # Ensure all keys exist (for upgrades)
            for k, v in _DEFAULT.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(_DEFAULT)


def _save(data: dict):
    os.makedirs(os.path.dirname(_STATS_FILE), exist_ok=True)
    with open(_STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _log_event(data: dict, event: str, detail: str = ""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["history"].append({"time": ts, "event": event, "detail": detail})
    # Keep last 200 events
    data["history"] = data["history"][-200:]


# ── Public API ────────────────────────────────────────────────

def get_all() -> dict:
    return _load()


def increment(key: str, amount: int = 1, event: str = "", detail: str = ""):
    data = _load()
    data[key] = data.get(key, 0) + amount
    if event:
        _log_event(data, event, detail)
    _save(data)


def record_password_cracked(password: str, algo: str):
    increment("passwords_cracked", event="✅ Password Cracked",
              detail=f"Algorithm: {algo} | Password: {password[:3]}***")
    increment("crack_attempts")


def record_crack_attempt():
    increment("crack_attempts")


def record_email_analyzed(risk_level: str = ""):
    increment("emails_analyzed", event="📧 Email Analyzed", detail=f"Risk: {risk_level}")


def record_phishing_detected():
    increment("phishing_emails_detected",
              event="🚨 Phishing Detected", detail="Email flagged as phishing")


def record_phishing_sent(target: str, template: str):
    increment("phishing_emails_sent",
              event="🎣 Phishing Email Sent",
              detail=f"Template: {template} → {target}")


def record_password_analyzed():
    increment("passwords_analyzed", event="🔑 Password Analyzed")


def record_breach_checked():
    increment("breaches_checked", event="🔍 Breach Check")


def reset_all():
    data = dict(_DEFAULT)
    data["last_reset"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["history"] = [{"time": data["last_reset"], "event": "🔄 Stats Reset", "detail": "All counters cleared"}]
    _save(data)

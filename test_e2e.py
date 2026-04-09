"""
E2E verification script for SmartWardrobe API.
Run with: python test_e2e.py
Assumes server is running at http://localhost:8000.
"""
import sys
import time
import json
import urllib.request
import urllib.error
import urllib.parse

BASE = "http://localhost:8000"
results = []  # (name, passed, detail)


# ── helpers ──────────────────────────────────────────────────────────────────

def request(method, path, body=None, token=None, form=False):
    url = BASE + path
    headers = {}
    data = None

    if body is not None and form:
        data = urllib.parse.urlencode(body).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except urllib.error.URLError as e:
        return None, str(e.reason)


def record(name, passed, detail=""):
    results.append((name, passed, detail))


def print_table():
    print("\n" + "=" * 70)
    print(f"{'TEST':<45} {'RESULT':<8} DETAIL")
    print("=" * 70)
    all_passed = True
    for name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{name:<45} {status:<8} {detail}")
    print("=" * 70)
    print("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED")
    print()
    return all_passed


def abort(reason):
    print(f"\n[ABORT] {reason}")
    print_table()
    sys.exit(1)


# ── Step 0: connectivity check ────────────────────────────────────────────────

print("Checking server connectivity...")
status, body = request("GET", "/health")
if status is None:
    abort("Connection refused — is the server running at http://localhost:8000?")
if status != 200:
    abort(f"Health check returned HTTP {status}: {body}")
print(f"  Server OK: {body}\n")


# ── Step 1: Auth ─────────────────────────────────────────────────────────────

unique_email = f"e2e_{int(time.time())}@test.com"
password = "E2ePass123!"

print(f"[1] Registering {unique_email} ...")
status, body = request("POST", "/auth/register",
                       {"email": unique_email, "password": password})
passed = status == 201 and "id" in body and body.get("email") == unique_email
record("1a. Register new user", passed,
       f"HTTP {status}" if passed else f"HTTP {status} — {body}")
if not passed:
    abort("Registration failed; cannot continue.")

print(f"[1] Logging in ...")
status, body = request("POST", "/auth/login",
                       {"username": unique_email, "password": password},
                       form=True)
token = body.get("access_token") if isinstance(body, dict) else None
passed = status == 200 and token is not None
record("1b. Login and receive JWT", passed,
       f"token={token[:20]}..." if passed else f"HTTP {status} — {body}")
if not passed:
    abort("Login failed; cannot continue.")


# ── Step 2: Empty wardrobe test ───────────────────────────────────────────────

print("[2] Testing empty wardrobe guard ...")
status, body = request("POST", "/outfits/generate",
                       {"occasion": "Casual"}, token=token)
detail_msg = body.get("detail", "") if isinstance(body, dict) else str(body)
passed = (
    status == 400
    and "2" in detail_msg  # "At least 2 clothing items..."
)
record("2.  Empty wardrobe → HTTP 400", passed,
       f"HTTP {status}: {detail_msg[:60]}" if not passed else detail_msg[:60])


# ── Step 3: Color validation ──────────────────────────────────────────────────

print("[3] Testing color_code validation ...")
status, body = request("POST", "/clothing/",
                       {"category": "Top", "sub_category": "Tank",
                        "color_code": "red", "material": "Cotton",
                        "season": ["summer"]},
                       token=token)
passed = status == 422
record("3.  color_code='red' → HTTP 422", passed,
       f"HTTP {status}" if passed else f"HTTP {status} — {body}")


# ── Step 4: Data setup ────────────────────────────────────────────────────────

items_to_add = [
    {"category": "Top",    "sub_category": "Shirt", "color_code": "#0000FF",
     "material": "Cotton", "season": ["spring", "summer"]},
    {"category": "Bottom", "sub_category": "Pants", "color_code": "#000000",
     "material": "Denim",  "season": ["spring", "autumn"]},
    {"category": "Shoes",  "sub_category": "Sneakers", "color_code": "#FFFFFF",
     "material": "Leather","season": ["spring", "summer", "autumn"]},
]

added_ids = []
print("[4] Adding 3 clothing items ...")
for item in items_to_add:
    status, body = request("POST", "/clothing/", item, token=token)
    if status == 201 and "id" in body:
        added_ids.append(body["id"])

passed = len(added_ids) == 3
record("4.  Add 3 clothing items", passed,
       f"Created {len(added_ids)}/3" if not passed else f"IDs: {', '.join(i[:8] for i in added_ids)}...")
if not passed:
    abort("Could not create test clothing items; cannot continue.")


# ── Step 5: Generate outfit ───────────────────────────────────────────────────

print("[5] Generating outfit ...")
status, body = request("POST", "/outfits/generate",
                       {"occasion": "Casual"}, token=token)

outfit_id = body.get("id") if isinstance(body, dict) else None
has_name = bool(body.get("name")) if isinstance(body, dict) else False
has_explanation = body.get("ai_explanation") not in (None, "") if isinstance(body, dict) else False
clothing_items = body.get("clothing_items", []) if isinstance(body, dict) else []
has_enough_items = len(clothing_items) >= 2

passed = status == 201 and has_name and has_explanation and has_enough_items
detail = (
    f"HTTP {status}, name={bool(has_name)}, "
    f"ai_explanation={bool(has_explanation)}, "
    f"clothing_items={len(clothing_items)}"
)
record("5.  Generate outfit → HTTP 201", passed, detail)

if not passed:
    print(f"     Response body: {json.dumps(body, indent=2)}")
    abort("Outfit generation failed; cannot continue to persistence test.")

print(f"     Outfit name   : {body.get('name')}")
print(f"     AI score      : {body.get('ai_score')}")
print(f"     Explanation   : {body.get('ai_explanation', '')[:80]}...")
print(f"     Items selected: {len(clothing_items)}")


# ── Step 6: Persistence check ─────────────────────────────────────────────────

print("[6] Verifying outfit persisted in GET /outfits/ ...")
status, body = request("GET", "/outfits/", token=token)
outfit_ids = [o["id"] for o in body] if isinstance(body, list) else []
passed = status == 200 and outfit_id in outfit_ids
record("6.  Outfit persisted in GET /outfits/", passed,
       f"Found {len(outfit_ids)} outfit(s)" if passed
       else f"HTTP {status}, outfit_id not in list: {outfit_ids}")


# ── Final table ───────────────────────────────────────────────────────────────

all_ok = print_table()
sys.exit(0 if all_ok else 1)

"""Minimal OAuth 1.0a client for the X API (stdlib only).

Usage:
  python xapi.py me                 # GET /2/users/me (疎通確認)
  python xapi.py post "text here"   # POST /2/tweets
"""
import sys, os, json, time, hmac, hashlib, base64, secrets, urllib.parse, urllib.request
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SECRETS = os.path.join(os.path.dirname(__file__), "..", ".secrets", "x-api.txt")

def load_keys():
    kv = {}
    with open(SECRETS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                kv[k] = v
    return kv

def pct(s):
    return urllib.parse.quote(s, safe="~")

def oauth_request(method, url, json_body=None):
    k = load_keys()
    oauth = {
        "oauth_consumer_key": k["CONSUMER_KEY"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": k["ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }
    # signature base string (JSON body is not part of OAuth1 signing)
    params = "&".join(f"{pct(a)}={pct(b)}" for a, b in sorted(oauth.items()))
    base = "&".join([method, pct(url), pct(params)])
    key = f"{pct(k['CONSUMER_SECRET'])}&{pct(k['ACCESS_SECRET'])}".encode()
    sig = base64.b64encode(hmac.new(key, base.encode(), hashlib.sha1).digest()).decode()
    oauth["oauth_signature"] = sig
    header = "OAuth " + ", ".join(f'{pct(a)}="{pct(b)}"' for a, b in sorted(oauth.items()))
    data = json.dumps(json_body).encode() if json_body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", header)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            print(r.status, r.read().decode())
    except urllib.error.HTTPError as e:
        print(e.code, e.read().decode())

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
    if cmd == "me":
        oauth_request("GET", "https://api.x.com/2/users/me")
    elif cmd == "post":
        oauth_request("POST", "https://api.x.com/2/tweets", {"text": sys.argv[2]})

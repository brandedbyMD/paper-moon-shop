"""毎日1件、queue.txt の先頭の投稿をXにポストする（Windowsタスクスケジューラから起動）。

- キューが空なら何もしない
- 成功した投稿は done.txt に移動、ログは post-log.txt
"""
import os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QUEUE = os.path.join(HERE, "..", "products", "sns", "queue.txt")
DONE = os.path.join(HERE, "..", "products", "sns", "done.txt")
LOG = os.path.join(HERE, "..", "products", "sns", "post-log.txt")
SEP = "=====POST====="

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}\n")

def main():
    dry = "--dry" in sys.argv
    if not os.path.exists(QUEUE):
        log("queue file missing"); return
    raw = open(QUEUE, encoding="utf-8").read()
    posts = [p.strip() for p in raw.split(SEP) if p.strip()]
    if not posts:
        log("queue empty - nothing to post"); return
    text, rest = posts[0], posts[1:]
    if dry:
        log(f"DRY RUN would post: {text[:40]!r}..."); return
    import xapi
    import io, contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            xapi.oauth_request("POST", "https://api.x.com/2/tweets", {"text": text})
        out = buf.getvalue().strip()
    except Exception as e:
        log(f"ERROR: {e}"); return
    if out.startswith("201"):
        with open(DONE, "a", encoding="utf-8") as f:
            f.write(SEP + "\n" + text + "\n")
        with open(QUEUE, "w", encoding="utf-8") as f:
            for p in rest:
                f.write(SEP + "\n" + p + "\n")
        log(f"posted ok: {out[:120]}")
    else:
        log(f"post failed: {out[:200]}")

if __name__ == "__main__":
    main()

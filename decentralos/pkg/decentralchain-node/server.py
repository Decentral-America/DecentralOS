#!/usr/bin/python3
"""DecentralOS node dashboard.

A small local web app that is the whole owner experience: one-step node setup,
live status, plain-language alerts, staking and network help, and phone pairing.
The screen shows it full-screen as the kiosk; a phone reaches it over the LAN
after scanning the pairing QR code.

Runs as the unprivileged `decentralchain` user. It never needs root: it writes
the node's config, and a systemd path unit restarts the node when that changes.
"""

import hashlib
import ipaddress
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = 6870
HERE = os.path.dirname(os.path.abspath(__file__))
SHARE = os.environ.get("DCC_SHARE", "/usr/share/decentralchain")
CONF_DIR = os.environ.get("DCC_CONF_DIR", "/etc/decentralchain")
DATA_DIR = os.environ.get("DCC_DATA_DIR", "/var/lib/decentralchain")
CONF = os.path.join(CONF_DIR, "dcc.conf")
API_KEY_FILE = os.path.join(CONF_DIR, "api-key")
TOKEN_FILE = os.path.join(DATA_DIR, "dashboard-token")
NODE_API = "http://127.0.0.1:6869"
SERVICE = "decentralchain-node.service"
STAKE_NEEDED = 1000  # DCC held or leased before a node may generate blocks
UNIT = 10**8

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58(data: bytes) -> str:
    n, out = int.from_bytes(data, "big"), ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    return "1" * (len(data) - len(data.lstrip(b"\0"))) + out


def unbase58(text: str) -> bytes:
    n = 0
    for c in text:
        n = n * 58 + B58.index(c)
    return n.to_bytes((n.bit_length() + 7) // 8, "big")


# Keccak-256 (the pre-standard SHA-3 the node uses); hashlib only has the final SHA-3.
_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]
_ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
_M = (1 << 64) - 1


def _rol(x, n):
    return ((x << n) | (x >> (64 - n))) & _M if n else x


def keccak256(data: bytes) -> bytes:
    rate = 136
    p = bytearray(data)
    p.append(0x01)
    p.extend(b"\0" * (-len(p) % rate))
    p[-1] |= 0x80
    a = [[0] * 5 for _ in range(5)]
    for off in range(0, len(p), rate):
        for i in range(rate // 8):
            a[i % 5][i // 5] ^= int.from_bytes(p[off + 8 * i : off + 8 * i + 8], "little")
        for rc in _RC:
            c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
            d = [c[(x - 1) % 5] ^ _rol(c[(x + 1) % 5], 1) for x in range(5)]
            a = [[a[x][y] ^ d[x] for y in range(5)] for x in range(5)]
            b = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    b[y][(2 * x + 3 * y) % 5] = _rol(a[x][y], _ROT[x][y])
            a = [[b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
            a[0][0] ^= rc
    return b"".join(a[i % 5][i // 5].to_bytes(8, "little") for i in range(4))


def secure_hash(data: bytes) -> bytes:
    return keccak256(hashlib.blake2b(data, digest_size=32).digest())


def run(*cmd, timeout=8):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def node(path, key=None, timeout=3):
    req = urllib.request.Request(NODE_API + path)
    if key:
        req.add_header("X-API-Key", key)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return ""


def write_private(path, text):
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o640)
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def token():
    t = read(TOKEN_FILE)
    if not t:
        t = secrets.token_urlsafe(18)
        write_private(TOKEN_FILE, t)
    return t


def network():
    route = run("ip", "-4", "route", "get", "1.1.1.1")
    parts = route.split()
    ip = parts[parts.index("src") + 1] if "src" in parts else ""
    dev = parts[parts.index("dev") + 1] if "dev" in parts else ""
    kind = "wifi" if dev.startswith("wl") else "wired" if dev else "none"
    online = False
    if ip:
        try:
            socket.create_connection(("1.1.1.1", 443), timeout=2).close()
            online = True
        except OSError:
            pass
    return {"ip": ip, "kind": kind, "online": online}


_cache = {}


def cached(name, ttl, fn):
    hit = _cache.get(name)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    value = fn()
    _cache[name] = (time.time(), value)
    return value


def new_phrase():
    with open(os.path.join(SHARE, "seed-words.txt")) as f:
        words = f.read().split()
    return " ".join(secrets.choice(words) for _ in range(15))


def provision(phrase):
    """Write the node's config. The path unit sees the new file and starts the node."""
    api_key = secrets.token_hex(24)
    name = "DecentralOS-" + secrets.token_hex(2)
    conf = f"""# Written by the DecentralOS dashboard.
# The chain itself (genesis, peers, protocol settings) comes from the packaged file.
include file("{SHARE}/conf/mainnet.conf")

dcc {{
  network.node-name = "{name}"

  wallet {{
    password = "{secrets.token_hex(24)}"
    seed = "{base58(phrase.encode())}"
  }}

  rest-api {{
    enable = yes
    bind-address = "127.0.0.1"
    port = 6869
    api-key-hash = "{base58(secure_hash(api_key.encode()))}"
  }}

  miner.enable = yes
}}
"""
    try:
        os.remove(os.path.join(DATA_DIR, "wallet", "wallet.dat"))
    except OSError:
        pass
    write_private(API_KEY_FILE, api_key + "\n")
    write_private(CONF, conf)


def alerts(s):
    out = []

    def add(level, title, fix):
        out.append({"level": level, "title": title, "fix": fix})

    net = s["net"]
    if net["kind"] == "none":
        add("bad", "This box is not connected to a network",
            "Plug an Ethernet cable from your router into the box, or join Wi-Fi from the Network section below.")
    elif not net["online"]:
        add("bad", "No internet connection",
            "The box is on your network but cannot reach the internet. Check that your router is online, then wait a minute.")
    if s["state"] == "offline":
        add("bad", "Your node has stopped",
            "It normally restarts by itself within a minute. If this message stays, unplug the box, wait ten seconds and plug it back in.")
    if s["state"] in ("syncing", "synced") and s["peers"] == 0 and net["online"]:
        add("warn", "Not connected to any other nodes yet",
            "This is normal for the first few minutes. If it lasts longer than half an hour, restart your router.")
    if s["state"] == "syncing":
        add("info", "Catching up with the network",
            "Your node is downloading the blockchain. This can take many hours the first time. Leave the box on; nothing else is needed.")
    if s["disk"]["free_gb"] < 10:
        add("bad", "Storage is almost full",
            f"Only {s['disk']['free_gb']} GB is left. Contact support before the node runs out of room.")
    if s["state"] == "synced" and s["generating"] < STAKE_NEEDED:
        add("info", "Not earning rewards yet",
            f"Your node needs {STAKE_NEEDED:,} DCC held or leased to it. See Earning rewards below.")
    return out


def status():
    s = {
        "configured": os.path.exists(CONF), "state": "unconfigured", "height": 0, "peers": 0,
        "behind": 0, "progress": 0, "address": "", "balance": 0, "generating": 0,
        "needed": STAKE_NEEDED, "version": "",
    }
    s["net"] = cached("net", 10, network)
    usage = shutil.disk_usage(DATA_DIR if os.path.isdir(DATA_DIR) else "/")
    s["disk"] = {"free_gb": usage.free // 2**30, "total_gb": usage.total // 2**30}
    if s["configured"]:
        try:
            s["height"] = node("/node/status")["blockchainHeight"]
            s["peers"] = len(node("/peers/connected")["peers"])
            last = node("/blocks/headers/last")["timestamp"] / 1000
            first = cached("genesis", 86400, lambda: node("/blocks/headers/at/1")["timestamp"] / 1000)
            now = time.time()
            s["behind"] = max(0, int(now - last))
            s["progress"] = round(min(100, 100 * (last - first) / max(1, now - first)), 1)
            s["state"] = "synced" if s["behind"] < 180 else "syncing"
            s["version"] = cached("version", 3600, lambda: node("/node/version")["version"])
            addresses = node("/addresses")
            if addresses:
                s["address"] = addresses[0]
                bal = node("/addresses/balance/details/" + addresses[0])
                s["balance"] = bal["regular"] / UNIT
                s["generating"] = bal["generating"] / UNIT
        except Exception:
            active = run("systemctl", "is-active", SERVICE) in ("active", "activating")
            fresh = time.time() - os.path.getmtime(CONF) < 300
            s["state"] = "starting" if active or fresh else "offline"
    s["alerts"] = alerts(s)
    return s


def qr_svg(text):
    return run("qrencode", "-t", "SVG", "-m", "2", "-o", "-", text)


class Handler(BaseHTTPRequestHandler):
    server_version = "DecentralOS"
    pending_phrase = None
    lock = threading.Lock()

    def log_message(self, *args):
        pass

    def local(self):
        return ipaddress.ip_address(self.client_address[0]).is_loopback

    def allowed(self, query):
        """Loopback is the kiosk. Anything else must be on the LAN and hold the pairing token."""
        addr = ipaddress.ip_address(self.client_address[0])
        if addr.is_loopback:
            return True
        if not addr.is_private:
            return False
        cookie = self.headers.get("Cookie", "")
        given = query.get("t", [""])[0] or next(
            (c.split("=", 1)[1] for c in cookie.replace(" ", "").split(";") if c.startswith("dos=")), "")
        return bool(given) and secrets.compare_digest(given, token())

    def send(self, code, body, ctype="application/json", headers=()):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def json(self, obj, code=200):
        self.send(code, json.dumps(obj))

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if not self.allowed(query):
            return self.send(403, "<h2>Scan the QR code on your DecentralOS screen to connect this device.</h2>", "text/html")
        if url.path == "/":
            if "t" in query:  # first visit from the QR code: keep the token in a cookie, drop it from the URL
                return self.send(302, "", headers=[
                    ("Set-Cookie", f"dos={token()}; Max-Age=31536000; HttpOnly; SameSite=Strict; Path=/"),
                    ("Location", "/")])
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                return self.send(200, f.read(), "text/html; charset=utf-8")
        if url.path == "/api/status":
            s = status()
            s["local"] = self.local()
            return self.json(s)
        if url.path == "/api/qr":
            kind = query.get("kind", [""])[0]
            if kind == "pair":
                ip = cached("net", 10, network)["ip"]
                text = f"http://{ip}:{PORT}/?t={token()}" if ip else ""
            else:
                text = status()["address"]
            return self.send(200, qr_svg(text) if text else "<svg xmlns='http://www.w3.org/2000/svg'/>", "image/svg+xml")
        if url.path == "/api/setup/phrase":
            if os.path.exists(CONF):
                return self.json({"error": "already set up"}, 409)
            with self.lock:
                Handler.pending_phrase = Handler.pending_phrase or new_phrase()
                return self.json({"phrase": Handler.pending_phrase})
        if url.path == "/api/seed":
            if not self.local():
                return self.json({"error": "The recovery phrase can only be shown on the box's own screen."}, 403)
            try:
                seed = node("/wallet/seed", key=read(API_KEY_FILE))["seed"]
                return self.json({"phrase": unbase58(seed).decode(errors="replace")})
            except Exception:
                return self.json({"error": "The node is not running yet. Try again in a minute."}, 503)
        if url.path == "/api/wifi":
            if not self.local():
                return self.json({"error": "local only"}, 403)
            seen, nets = set(), []
            for line in run("nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", timeout=20).splitlines():
                ssid, _, rest = line.rpartition(":")[0].rpartition(":")
                if ssid and ssid not in seen:
                    seen.add(ssid)
                    nets.append({"ssid": ssid.replace("\\:", ":"), "signal": int(rest or 0)})
            return self.json({"networks": sorted(nets, key=lambda n: -n["signal"])[:15]})
        self.send(404, "{}")

    def do_POST(self):
        url = urlparse(self.path)
        # A custom header cannot be sent cross-site without a preflight we never grant,
        # so another web page cannot drive these endpoints from the owner's browser.
        if not self.allowed({}) or self.headers.get("X-DecentralOS") != "1":
            return self.json({"error": "forbidden"}, 403)
        try:
            body = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 65536)) or b"{}")
        except ValueError:
            return self.json({"error": "bad request"}, 400)
        if url.path == "/api/setup":
            with self.lock:
                if os.path.exists(CONF):
                    return self.json({"error": "already set up"}, 409)
                phrase = " ".join(str(body.get("phrase") or "").split()) or Handler.pending_phrase
                if not phrase or len(phrase) < 20:
                    return self.json({"error": "That recovery phrase is too short."}, 400)
                provision(phrase)
                Handler.pending_phrase = None
            return self.json({"ok": True})
        if url.path == "/api/wifi":
            if not self.local():
                return self.json({"error": "local only"}, 403)
            ssid, password = str(body.get("ssid") or ""), str(body.get("password") or "")
            cmd = ["nmcli", "device", "wifi", "connect", ssid] + (["password", password] if password else [])
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            except (OSError, subprocess.SubprocessError):
                return self.json({"error": "Could not join that network."}, 500)
            _cache.pop("net", None)
            if r.returncode:
                return self.json({"error": "Could not join. Check the password and try again."}, 400)
            return self.json({"ok": True})
        self.send(404, "{}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        assert keccak256(b"").hex() == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
        assert base58(b"hello world") == "StV1DL6CwTryKyV" and unbase58("StV1DL6CwTryKyV") == b"hello world"
        print(base58(secure_hash(sys.argv[2].encode())) if len(sys.argv) > 2 else "ok")
        sys.exit(0)
    ThreadingHTTPServer.address_family = socket.AF_INET
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

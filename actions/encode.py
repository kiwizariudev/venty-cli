"""
actions/encode.py — base64, md5, sha256 encoding/hashing
"""
import base64
import hashlib


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


ACTIONS = {
    "os_base64_encode": {
        "description": "Base64 encode a string, args = [text]",
        "execute": lambda a: _stdout(base64.b64encode(a[0].encode()).decode()),
    },
    "os_base64_decode": {
        "description": "Base64 decode a string, args = [base64_text]",
        "execute": lambda a: _stdout(base64.b64decode(a[0]).decode()),
    },
    "os_md5_string": {
        "description": "Get MD5 hash of a string, args = [text]",
        "execute": lambda a: _stdout(hashlib.md5(a[0].encode()).hexdigest()),
    },
    "os_sha256_string": {
        "description": "Get SHA256 hash of a string, args = [text]",
        "execute": lambda a: _stdout(hashlib.sha256(a[0].encode()).hexdigest()),
    },
    "os_sha1_string": {
        "description": "Get SHA1 hash of a string, args = [text]",
        "execute": lambda a: _stdout(hashlib.sha1(a[0].encode()).hexdigest()),
    },
}

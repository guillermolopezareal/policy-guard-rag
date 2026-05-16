import sys
import httpx

filename = sys.argv[1] if len(sys.argv) > 1 else "samples/sample_security_policy.txt"

with open(filename, "rb") as f:
    r = httpx.post(
        "http://localhost:8000/ingest",
        files={"file": (filename.split("/")[-1].split("\\")[-1], f, "text/plain")},
    )

print(r.json())

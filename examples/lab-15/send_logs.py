"""Jednorazowy import do lokalnego tunelu Loki, ze znacznikiem czasu importu."""
import json
import sys
import time
from urllib.request import Request, urlopen


def make_payload(lines, now):
    values = [[str(now + i), line.rstrip("\n")] for i, line in enumerate(lines) if line.strip()]
    return {"streams": [{"stream": {"job": "incidentflow-lab", "source": "manual-import"}, "values": values}]}


def main():
    lines = sys.stdin.readlines()
    if not 1 <= len(lines) <= 200:
        raise SystemExit("Podaj od 1 do 200 linii przez stdin.")
    payload = make_payload(lines, time.time_ns())
    if not payload["streams"][0]["values"]:
        raise SystemExit("Brak niepustych linii.")
    request = Request("http://127.0.0.1:13100/loki/api/v1/push", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        print("HTTP", response.status)


if __name__ == "__main__":
    main()

"""Simple health check script."""

import sys

import httpx


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    try:
        response = httpx.get(f"{url}/health", timeout=10)
        data = response.json()
        print(f"Status: {data['status']}")
        for key, value in data.items():
            if key != "status":
                print(f"  {key}: {value}")
        sys.exit(0 if data["status"] == "ok" else 1)
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

import os
import sys
import argparse
import uvicorn
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    parser = argparse.ArgumentParser(description="Run Local Character.AI Web Application")
    default_port = int(os.environ.get("PORT", 8000))
    default_host = os.environ.get("HOST", "0.0.0.0")

    parser.add_argument("--port", type=int, default=default_port, help=f"Port to bind server (default: {default_port})")
    parser.add_argument("--host", type=str, default=default_host, help=f"Host address to bind (default: {default_host})")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")

    args = parser.parse_args()

    print("=" * 65)
    print(" 🎭 LOCAL CHARACTER.AI WEB APPLICATION")
    print(f" Serving at: http://{args.host}:{args.port}")
    print(f" Local Web:  http://127.0.0.1:{args.port}")
    print(" Powered by: Python, FastAPI, SQLite & Vanilla HTML/JS")
    print("=" * 65)

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()

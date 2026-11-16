
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading

PROJECT_DIR = Path(__file__).resolve().parent
DASHBOARD_URL = "http://127.0.0.1:8000/src/dashboard/index.html"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=str(PROJECT_DIR),
            **kwargs
        )

server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)

print("Sweden Job Market Dashboard is running!")
print(DASHBOARD_URL)

threading.Timer(
    1,
    lambda: webbrowser.open(DASHBOARD_URL)
).start()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nDashboard stopped.")
finally:
    server.server_close()

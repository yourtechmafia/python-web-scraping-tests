import threading, time, http.server, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
hits = []
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        hits.append(time.monotonic())
        if len(hits) <= 2:
            self.send_response(429); self.send_header("Retry-After", "3"); self.end_headers()
        else:
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
srv = http.server.HTTPServer(("127.0.0.1", 8765), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"], respect_retry_after_header=True, raise_on_status=False)
s = requests.Session(); s.mount("http://", HTTPAdapter(max_retries=retry))
t = time.monotonic(); r = s.get("http://127.0.0.1:8765/", timeout=10)
print(r.status_code, f"{time.monotonic()-t:.1f}s", "gaps:", [round(b-a,1) for a,b in zip(hits, hits[1:])])
srv.shutdown()

import requests
from curl_cffi import requests as curl_requests

URL = "https://tls.browserleaks.com/json"

plain = requests.get(URL, timeout=15).json()
chrome = curl_requests.get(URL, impersonate="chrome", timeout=15).json()

for label, data in [("requests", plain), ("curl_cffi (chrome)", chrome)]:
    print(label)
    print("  JA4:       ", data["ja4"])
    print("  HTTP/2 fp: ", data.get("akamai_hash") or "none (HTTP/1.1)")
    print("  User-Agent:", data["user_agent"])

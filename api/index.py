from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException, TimeoutException, DuckDuckGoSearchException

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        # FIX: Clean the path and extract only the final segment
        path_segments = [seg for seg in parsed_url.path.split('/') if seg]
        
        # If the path ends in index.py, check the segment right before it, or default to text
        if path_segments and path_segments[-1] == "index.py":
            path = path_segments[-2] if len(path_segments) > 1 else "text"
        else:
            path = path_segments[-1] if path_segments else "text"
            
        query_params = parse_qs(parsed_url.query)
        query = query_params.get('q', [None])
        max_results = int(query_params.get('max',))

        if not query:
            self.send_json_response(400, {"error": "Missing required query parameter 'q'"})
            return

        try:
            with DDGS(timeout=15) as ddgs:
                # The path matching will now correctly intercept your routes
                if path == "text" or path == "api":
                    results = list(ddgs.text(query, max_results=max_results))
                elif path == "images":
                    results = list(ddgs.images(query, max_results=max_results))
                elif path == "news":
                    results = list(ddgs.news(query, max_results=max_results))
                else:
                    self.send_json_response(404, {"error": f"Endpoint '/{path}' not found. Use /text, /images, or /news."})
                    return
            
            self.send_json_response(200, results)
            
        except RatelimitException:
            self.send_json_response(429, {"error": "Rate limit exceeded", "message": "DuckDuckGo throttled this IP. Retry in 60s."})
        except TimeoutException:
            self.send_json_response(504, {"error": "Timeout error", "message": "The upstream search engine timed out."})
        except DuckDuckGoSearchException as e:
            self.send_json_response(502, {"error": "Search exception", "message": str(e)})
        except Exception as e:
            self.send_json_response(500, {"error": "Internal server error", "message": str(e)})

    def send_json_response(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

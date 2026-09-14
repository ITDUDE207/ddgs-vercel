from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from duckduckgo_search import DDGS

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Parse URL structure and parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path.strip('/')
        query_params = parse_qs(parsed_url.query)
        
        query = query_params.get('q', [None])
        max_results = int(query_params.get('max', [5]))

        # Check for missing search term
        if not query:
            self.send_json_response(400, {"error": "Missing required query parameter 'q'"})
            return

        try:
            with DDGS() as ddgs:
                # 2. Route requests dynamically based on the path URL
                if path == "" or path == "text":
                    results = list(ddgs.text(query, max_results=max_results))
                    
                elif path == "images":
                    results = list(ddgs.images(query, max_results=max_results))
                    
                elif path == "news":
                    results = list(ddgs.news(query, max_results=max_results))
                    
                else:
                    self.send_json_response(444, {"error": f"Endpoint '/{path}' not found. Use /text, /images, or /news."})
                    return
            
            # Send successful search payloads
            self.send_json_response(200, results)
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    # Helper method to streamline headers and status code outputs
    def send_json_response(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Enable frontend integrations (CORS)
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

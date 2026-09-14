from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from duckduckgo_search import DDGS

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query string parameters from URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Extract the search query 'q'
        query = query_params.get('q', [None])[0]
        # Extract 'max' results parameter (default to 5)
        max_results = int(query_params.get('max', [5])[0])

        if not query:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing required query parameter 'q'"}).encode('utf-8'))
            return

        try:
            # Query DuckDuckGo using the core library
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # Enable CORS so you can fetch this API from frontend apps
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

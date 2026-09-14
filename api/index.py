from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from duckduckgo_search import DDGS
# Import the explicit exceptions thrown by the underlying library
from duckduckgo_search.exceptions import RatelimitException, TimeoutException, DuckDuckGoSearchException

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path.strip('/')
        query_params = parse_qs(parsed_url.query)
        
        query = query_params.get('q', [None])
        max_results = int(query_params.get('max', [5])[0])

        if not query:
            self.send_json_response(400, {"error": "Missing required query parameter 'q'"})
            return

        try:
            # OPTIONAL: If you keep hitting 202/418 bans, sign up for a free proxy 
            # and uncomment the line below:
            # my_proxy = "http://your-proxy-provider.com"
            my_proxy = None 

            # Set a slightly higher timeout to prevent sudden Vercel drops
            with DDGS(proxy=my_proxy, timeout=15) as ddgs:
                if path == "" or path == "text":
                    results = list(ddgs.text(query, max_results=max_results))
                elif path == "images":
                    results = list(ddgs.images(query, max_results=max_results))
                elif path == "news":
                    results = list(ddgs.news(query, max_results=max_results))
                else:
                    self.send_json_response(404, {"error": f"Endpoint '/{path}' not found."})
                    return
            
            self.send_json_response(200, results)
            
        except RatelimitException:
            # Catching the common "too many requests" block safely
            self.send_json_response(429, {
                "error": "Rate limit exceeded", 
                "message": "DuckDuckGo is throttling this shared Vercel IP address. Please retry in 60 seconds."
            })
        except TimeoutException:
            self.send_json_response(504, {
                "error": "Timeout error", 
                "message": "The upstream search engine took too long to respond."
            })
        except DuckDuckGoSearchException as e:
            self.send_json_response(502, {
                "error": "Search library exception", 
                "message": str(e)
            })
        except Exception as e:
            self.send_json_response(500, {
                "error": "Internal server error", 
                "message": str(e)
            })

    def send_json_response(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

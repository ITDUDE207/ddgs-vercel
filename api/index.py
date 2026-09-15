from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from ddgs import DDGS

# Visual HTML documentation layout
DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSON Search API — Documentation</title>
    <style>
        :root {
            --bg: #0f172a; --surface: #1e293b; --border: #334155;
            --text: #f8fafc; --text-muted: #94a3b8; --accent: #38bdf8;
            --accent-bg: rgba(56, 189, 248, 0.1);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: var(--bg); color: var(--text); font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; padding: 2rem 1rem; }
        .container { max-width: 800px; margin: 0 auto; }
        header { margin-bottom: 2.5rem; text-align: center; }
        h1 { font-size: 2.25rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -0.025em; }
        p.subtitle { color: var(--text-muted); font-size: 1.1rem; }
        h2 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
        .endpoint-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.75rem; }
        .badge.get { background: var(--accent-bg); color: var(--accent); border: 1px solid var(--accent); }
        .url-structure { font-family: monospace; font-size: 1rem; background: #090d16; padding: 0.75rem 1rem; border-radius: 8px; overflow-x: auto; color: #e2e8f0; margin-bottom: 1rem; }
        .url-structure span { color: var(--accent); }
        ul { list-style: none; padding-left: 0; }
        li { margin-bottom: 0.5rem; color: var(--text-muted); }
        strong { color: var(--text); font-family: monospace; }
        a { color: var(--accent); text-decoration: none; }
        a:hover { text-decoration: underline; }
        footer { margin-top: 3rem; text-align: center; color: var(--text-muted); font-size: 0.9rem; border-top: 1px solid var(--border); padding-top: 1.5rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Live Search JSON API</h1>
            <p class="subtitle">A fast, keyless serverless proxy wrapper for web scraping extraction endpoints.</p>
        </header>

        <h2>API Endpoints</h2>
        
        <div class="endpoint-card">
            <span class="badge get">GET</span>
            <div class="url-structure">/text?q=<span>{query}</span>&max=<span>{count}</span></div>
            <p style="margin-bottom: 0.75rem;">Fetches standard text-based web search engine organic results.</p>
            <ul>
                <li>• <strong>q</strong> (Required): The search keyword string.</li>
                <li>• <strong>max</strong> (Optional): Limit total returned arrays (Default: 5).</li>
            </ul>
            <p style="margin-top: 0.75rem; font-size: 0.9rem;"><a href="./text?q=artificial+intelligence&max=3" target="_blank">👉 Try Live Web Example</a></p>
        </div>

        <div class="endpoint-card">
            <span class="badge get">GET</span>
            <div class="url-structure">/images?q=<span>{query}</span>&max=<span>{count}</span></div>
            <p style="margin-bottom: 0.75rem;">Extracts image URLs, heights, widths, and structural target sources.</p>
            <ul>
                <li>• <strong>q</strong> (Required): The search keyword string.</li>
                <li>• <strong>max</strong> (Optional): Limit total returned arrays (Default: 5).</li>
            </ul>
            <p style="margin-top: 0.75rem; font-size: 0.9rem;"><a href="./images?q=australian+beaches&max=3" target="_blank">👉 Try Live Image Example</a></p>
        </div>

        <div class="endpoint-card">
            <span class="badge get">GET</span>
            <div class="url-structure">/news?q=<span>{query}</span>&max=<span>{count}</span></div>
            <p style="margin-bottom: 0.75rem;">Pulls context from recent indexing operations and mainstream current event arrays.</p>
            <ul>
                <li>• <strong>q</strong> (Required): The search keyword string.</li>
                <li>• <strong>max</strong> (Optional): Limit total returned arrays (Default: 5).</li>
            </ul>
            <p style="margin-top: 0.75rem; font-size: 0.9rem;"><a href="./news?q=technology&max=2" target="_blank">👉 Try Live News Example</a></p>
        </div>

        <footer>
            <p>Deploy infrastructure powered by Vercel Serverless Runtimes.</p>
        </footer>
    </div>
</body>
</html>
"""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Safely extract the query string parameter primitive
        query_list = query_params.get('q', [])
        query_str = query_list if query_list else None
        
        try:
            max_results = int(query_params.get('max',))
        except (ValueError, TypeError, IndexError):
            max_results = 5

        # Check endpoints path routing 
        path_segments = [seg for seg in parsed_url.path.lower().split('/') if seg]
        search_type = path_segments[-1] if path_segments and "index.py" not in path_segments[-1] else "text"

        # 1. Render documentation page if no query string is provided
        if not query_str:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(DOCS_HTML.encode('utf-8'))
            return

        # 2. Run scraping operations mapping to the correct new `query` variable names
        try:
            with DDGS(timeout=15) as ddgs:
                if search_type == "images":
                    results = list(ddgs.images(query=query_str, max_results=max_results))
                elif search_type == "news":
                    results = list(ddgs.news(query=query_str, max_results=max_results))
                else:
                    results = list(ddgs.text(query=query_str, max_results=max_results))
            
            self.send_json_response(200, results)
            
        except Exception as e:
            self.send_json_response(502, {
                "error": "Upstream scraper failure", 
                "details": str(e)
            })

    def send_json_response(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

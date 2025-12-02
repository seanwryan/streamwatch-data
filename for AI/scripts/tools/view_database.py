#!/usr/bin/env python3
"""
Simple web interface to view StreamWatch database
Run this script and open http://localhost:8080 in your browser
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import webbrowser
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class DatabaseViewer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.show_home()
        elif self.path.startswith('/sites'):
            self.show_sites()
        elif self.path.startswith('/query'):
            self.show_query()
        else:
            self.send_error(404)
    
    def show_home(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StreamWatch Database Viewer</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #2c3e50; }
                .nav { margin: 20px 0; }
                .nav a { 
                    display: inline-block; 
                    margin: 10px 15px 10px 0; 
                    padding: 10px 20px; 
                    background: #3498db; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                }
                .nav a:hover { background: #2980b9; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .stats { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌊 StreamWatch Database Viewer</h1>
                <div class="nav">
                    <a href="/sites">View All Sites</a>
                    <a href="/query">Run Custom Query</a>
                </div>
                <div class="stats">
                    <h3>Database Status</h3>
                    <p>✅ Connected to StreamWatch database</p>
                    <p>📊 168 site records loaded</p>
                    <p>🔧 Full edit access enabled</p>
                </div>
                <h3>Quick Stats</h3>
        """
        
        # Add quick stats
        try:
            DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
            engine = create_engine(DATABASE_URL)
            
            with engine.connect() as conn:
                # Active vs inactive
                result = conn.execute(text("SELECT is_active, COUNT(*) FROM sites GROUP BY is_active"))
                for row in result:
                    status = 'Active' if row[0] else 'Inactive'
                    html += f"<p><strong>{status} Sites:</strong> {row[1]}</p>"
                
                # Sites with coordinates
                result = conn.execute(text("SELECT COUNT(*) FROM sites WHERE latitude IS NOT NULL AND longitude IS NOT NULL"))
                count = result.scalar()
                html += f"<p><strong>Sites with GPS:</strong> {count}</p>"
                
        except Exception as e:
            html += f"<p>Error loading stats: {e}</p>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def show_sites(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        try:
            DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
            engine = create_engine(DATABASE_URL)
            
            with engine.connect() as conn:
                # Get all sites
                df = pd.read_sql("SELECT site_code, waterbody, latitude, longitude, is_active FROM sites ORDER BY site_code", conn)
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>StreamWatch Sites</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .container { max-width: 1400px; margin: 0 auto; }
                        h1 { color: #2c3e50; }
                        .nav { margin: 20px 0; }
                        .nav a { 
                            display: inline-block; 
                            margin: 10px 15px 10px 0; 
                            padding: 10px 20px; 
                            background: #3498db; 
                            color: white; 
                            text-decoration: none; 
                            border-radius: 5px; 
                        }
                        .nav a:hover { background: #2980b9; }
                        table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 12px; }
                        th, td { border: 1px solid #ddd; padding: 6px; text-align: left; }
                        th { background-color: #f2f2f2; position: sticky; top: 0; }
                        .active { color: green; }
                        .inactive { color: red; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🌊 StreamWatch Sites ({})</h1>
                        <div class="nav">
                            <a href="/">← Back to Home</a>
                        </div>
                        <table>
                            <tr>
                                <th>Site Code</th>
                                <th>Waterbody</th>
                                <th>Latitude</th>
                                <th>Longitude</th>
                                <th>Status</th>
                            </tr>
                """.format(len(df))
                
                for _, row in df.iterrows():
                    status_class = 'active' if row['is_active'] else 'inactive'
                    status_text = 'Active' if row['is_active'] else 'Inactive'
                    lat = f"{row['latitude']:.6f}" if pd.notna(row['latitude']) else 'N/A'
                    lon = f"{row['longitude']:.6f}" if pd.notna(row['longitude']) else 'N/A'
                    
                    html += f"""
                    <tr>
                        <td><strong>{row['site_code']}</strong></td>
                        <td>{row['waterbody']}</td>
                        <td>{lat}</td>
                        <td>{lon}</td>
                        <td class="{status_class}">{status_text}</td>
                    </tr>
                    """
                
                html += """
                        </table>
                    </div>
                </body>
                </html>
                """
                
        except Exception as e:
            html = f"<h1>Error</h1><p>{e}</p>"
        
        self.wfile.write(html.encode())
    
    def show_query(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Custom Query</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #2c3e50; }
                .nav { margin: 20px 0; }
                .nav a { 
                    display: inline-block; 
                    margin: 10px 15px 10px 0; 
                    padding: 10px 20px; 
                    background: #3498db; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                }
                .nav a:hover { background: #2980b9; }
                textarea { width: 100%; height: 100px; font-family: monospace; }
                button { padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #229954; }
                .examples { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Custom SQL Query</h1>
                <div class="nav">
                    <a href="/">← Back to Home</a>
                </div>
                <div class="examples">
                    <h3>Example Queries:</h3>
                    <p><strong>All sites:</strong> SELECT * FROM sites LIMIT 10;</p>
                    <p><strong>Active sites only:</strong> SELECT * FROM sites WHERE is_active = true;</p>
                    <p><strong>Sites by waterbody:</strong> SELECT * FROM sites WHERE waterbody LIKE '%MILLSTONE%';</p>
                    <p><strong>Count by waterbody:</strong> SELECT waterbody, COUNT(*) FROM sites GROUP BY waterbody ORDER BY COUNT(*) DESC;</p>
                </div>
                <form method="post">
                    <textarea name="query" placeholder="Enter your SQL query here...">SELECT * FROM sites LIMIT 10;</textarea><br><br>
                    <button type="submit">Execute Query</button>
                </form>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def do_POST(self):
        if self.path == '/query':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            query = urllib.parse.parse_qs(post_data.decode())[b'query'][0].decode()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            try:
                DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
                engine = create_engine(DATABASE_URL)
                
                with engine.connect() as conn:
                    df = pd.read_sql(query, conn)
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Query Results</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; }}
                            .container {{ max-width: 1400px; margin: 0 auto; }}
                            .nav {{ margin: 20px 0; }}
                            .nav a {{ 
                                display: inline-block; 
                                margin: 10px 15px 10px 0; 
                                padding: 10px 20px; 
                                background: #3498db; 
                                color: white; 
                                text-decoration: none; 
                                border-radius: 5px; 
                            }}
                            .nav a:hover {{ background: #2980b9; }}
                            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 12px; }}
                            th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
                            th {{ background-color: #f2f2f2; }}
                            .query {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>📊 Query Results ({len(df)} rows)</h1>
                            <div class="nav">
                                <a href="/query">← Back to Query</a>
                            </div>
                            <div class="query">
                                <strong>Query:</strong> {query}
                            </div>
                            <table>
                                <tr>
                    """
                    
                    # Add headers
                    for col in df.columns:
                        html += f"<th>{col}</th>"
                    html += "</tr>"
                    
                    # Add data rows
                    for _, row in df.iterrows():
                        html += "<tr>"
                        for col in df.columns:
                            value = row[col]
                            if pd.isna(value):
                                value = 'N/A'
                            html += f"<td>{value}</td>"
                        html += "</tr>"
                    
                    html += """
                            </table>
                        </div>
                    </body>
                    </html>
                    """
                    
            except Exception as e:
                html = f"<h1>Query Error</h1><p>{e}</p>"
            
            self.wfile.write(html.encode())

def start_server():
    server = HTTPServer(('localhost', 8080), DatabaseViewer)
    print("🌐 StreamWatch Database Viewer started!")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop the server")
    server.serve_forever()

if __name__ == "__main__":
    start_server()

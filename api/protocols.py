"""
Vercel Function handler for protocols endpoints.

This module provides the serverless function handler that wraps our FastAPI
protocols router for deployment on Vercel.
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Mock protocol data
        protocols = [
            {
                "id": "NCT12345678",
                "title": "Phase II Study of Novel Cancer Treatment",
                "status": "Recruiting",
                "phase": "Phase 2",
                "condition": "Breast Cancer",
                "sponsor": "University Medical Center",
                "location": "Multiple Sites",
                "enrollment": 150
            },
            {
                "id": "NCT87654321", 
                "title": "Cardiovascular Prevention Trial",
                "status": "Active",
                "phase": "Phase 3",
                "condition": "Heart Disease",
                "sponsor": "Pharma Corp",
                "location": "US & Canada",
                "enrollment": 500
            }
        ]
        
        response = {
            "protocols": protocols,
            "total": len(protocols),
            "status": "success"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
        return

 
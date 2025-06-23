#!/usr/bin/env python3
"""
WSGI entry point for the Universal Social Media Downloader application
"""

import os
import sys
from werkzeug.middleware.proxy_fix import ProxyFix

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Apply ProxyFix for deployment behind reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1, 
    x_proto=1, 
    x_host=1, 
    x_prefix=1
)

# Set production configurations
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'your-super-secret-key-change-this'),
    DEBUG=False,
    TESTING=False
)

if __name__ == "__main__":
    app.run()

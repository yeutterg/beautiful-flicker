"""Test script to verify Flask app can be imported."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask_app import app
    print("✓ Flask app module imported successfully")
    
    # Check if app is configured
    if app.app.config:
        print("✓ Flask app configured")
    
    # Check routes
    routes = []
    for rule in app.app.url_map.iter_rules():
        routes.append(str(rule))
    
    print(f"✓ Found {len(routes)} routes:")
    for route in sorted(routes):
        print(f"  - {route}")
    
    print("\n✅ Flask app structure looks good!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
#!/usr/bin/env python
"""
Minimal test to verify Django setup
"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful!")
    
    # Try to import models
    from stickforstats.core.models import User
    print("✅ Can import User model")
    
    # Check database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection works")
    
    print("\n🎉 Basic setup is working! Ready to deploy to Render.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
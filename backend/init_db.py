#!/usr/bin/env python3
"""
Database initialization script for MeTTa Self-Reflective RAG
Run this script to set up the database tables.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, User
from config import settings

def init_database():
    """Initialize the database with tables"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if database file exists
        db_path = settings.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        if os.path.exists(db_path):
            print(f"📁 Database file created at: {db_path}")
        else:
            print("⚠️  Database file not found. Check your configuration.")

if __name__ == "__main__":
    print("🚀 Initializing MeTTa Self-Reflective RAG Database...")
    init_database()
    print("✨ Database initialization complete!")

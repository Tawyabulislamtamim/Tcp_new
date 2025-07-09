#!/usr/bin/env python3
"""
Test script to verify metrics setup
"""
import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        print("✓ Backend dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing backend dependencies: {e}")
        return False

def install_backend_dependencies():
    """Install backend dependencies"""
    print("Installing backend dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            os.path.join("backend", "requirements.txt")
        ], check=True, cwd=os.getcwd())
        print("✓ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install frontend dependencies"""
    print("Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], check=True, cwd=os.path.join(os.getcwd(), "frontend"))
        print("✓ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install frontend dependencies: {e}")
        return False

def main():
    print("=== TCP File Transfer Project Setup ===")
    print()
    
    # Check current directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("✗ This script must be run from the project root directory")
        print("  Expected structure: project_root/backend/ and project_root/frontend/")
        return 1
    
    print("✓ Project structure found")
    
    # Check backend dependencies
    if not check_dependencies():
        if not install_backend_dependencies():
            return 1
        
        # Check again after installation
        if not check_dependencies():
            print("✗ Backend dependencies still not available after installation")
            return 1
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        return 1
    
    print()
    print("=== Setup Complete! ===")
    print()
    print("To run the project:")
    print("1. Backend:  cd backend && python app.py")
    print("2. Frontend: cd frontend && npm start")
    print()
    print("Or use Docker:")
    print("   docker-compose up")
    print()
    print("The metrics dashboard will be available at: http://localhost:3000")
    print("Backend API will be available at: http://localhost:5000")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

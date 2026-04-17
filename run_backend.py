#!/usr/bin/env python
"""
Bible Game Backend Startup Script
Handles port cleanup and proper server initialization
"""
import os
import sys
import subprocess
import socket
import time

def is_port_in_use(port=8000):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
        except:
            return False

def kill_port_process(port=8000):
    """Kill any process using the specified port"""
    if os.name == 'nt':  # Windows
        # Find and kill process using port
        os.system(f'taskkill /F /IM python.exe /FI "MEMUSAGE>100000" 2>nul')
        # More specific approach using netstat
        result = os.popen(f'netstat -ano | findstr :{port}').read()
        if result:
            try:
                pid = result.strip().split()[-1]
                os.system(f'taskkill /PID {pid} /F')
                time.sleep(1)  # Wait for port to be released
            except:
                pass

def main():
    """Main startup function"""
    print("[STARTUP] Bible Game Backend Server")
    print(f"[STARTUP] Working directory: {os.getcwd()}")
    
    # Change to src directory
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    if os.path.exists(src_dir):
        os.chdir(src_dir)
        print(f"[STARTUP] Changed to src directory: {os.getcwd()}")
    
    # Clean up any existing process on port 8000
    if is_port_in_use(8000):
        print("[STARTUP] Port 8000 is in use, cleaning up...")
        kill_port_process(8000)
        time.sleep(2)
    
    # Verify port is free
    if is_port_in_use(8000):
        print("[ERROR] Port 8000 is still in use after cleanup")
        print("[ERROR] Please manually kill the process using: taskkill /F /IM python.exe")
        sys.exit(1)
    
    print("[STARTUP] Port 8000 is available, starting server...")
    
    # Start the server
    try:
        import uvicorn
        from main import app
        
        print("[STARTUP] Launching uvicorn server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

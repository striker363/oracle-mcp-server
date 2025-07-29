#!/usr/bin/env python3
"""
Setup script for Oracle MCP Server
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def create_config():
    """Create config.json from example if it doesn't exist"""
    config_file = Path("config.json")
    example_file = Path("config.example.json")
    
    if config_file.exists():
        print("✅ config.json already exists")
        return
    
    if not example_file.exists():
        print("❌ config.example.json not found")
        sys.exit(1)
    
    print("📝 Creating config.json from example...")
    try:
        with open(example_file, 'r') as f:
            config = json.load(f)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ config.json created successfully")
        print("⚠️  Please edit config.json with your database credentials")
    except Exception as e:
        print(f"❌ Failed to create config.json: {e}")
        sys.exit(1)

def check_oracle_client():
    """Check if Oracle client is available"""
    print("🔍 Checking Oracle client availability...")
    try:
        import oracledb
        print("✅ Oracle Python driver (oracledb) is available")
    except ImportError:
        print("❌ Oracle Python driver not found")
        print("💡 Install with: pip install oracledb[thick]")
        print("💡 Or install Oracle Instant Client and add to PATH")

def main():
    """Main setup function"""
    print("🚀 Setting up Oracle MCP Server...")
    print("=" * 50)
    
    check_python_version()
    install_dependencies()
    create_config()
    check_oracle_client()
    
    print("=" * 50)
    print("✅ Setup completed!")
    print("📝 Next steps:")
    print("   1. Edit config.json with your database credentials")
    print("   2. Install Oracle Client Libraries if not already installed")
    print("   3. Run: python mcp_server.py")
    print("   4. Configure your MCP client to use this server")

if __name__ == "__main__":
    main() 
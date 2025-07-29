#!/usr/bin/env python3
"""
Development tool to run all Charlie Reporting services
Useful for local development and testing
"""

import asyncio
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# Service definitions
SERVICES = [
    {
        "name": "outlook-relay",
        "port": 8080,
        "directory": "services/outlook-relay",
        "command": ["python", "src/main.py"]
    },
    {
        "name": "database-service", 
        "port": 8081,
        "directory": "services/database-service",
        "command": ["python", "src/main.py"]
    },
    {
        "name": "scheduler-service",
        "port": 8082, 
        "directory": "services/scheduler-service",
        "command": ["python", "src/main.py"]
    },
    {
        "name": "report-generator",
        "port": 8083,
        "directory": "services/report-generator", 
        "command": ["python", "src/main.py"]
    },
    {
        "name": "email-service",
        "port": 8084,
        "directory": "services/email-service",
        "command": ["python", "src/main.py"]
    }
]

class ServiceRunner:
    """Manages running multiple services for development"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        
    def setup_shared_components(self):
        """Create symlinks to shared components in each service"""
        print("Setting up shared components...")
        
        shared_source = Path("shared").absolute()
        
        for service in SERVICES:
            service_dir = Path(service["directory"])
            if not service_dir.exists():
                print(f"⚠️  Service directory {service_dir} does not exist, skipping")
                continue
                
            shared_link = service_dir / "shared"
            
            # Remove existing symlink if it exists
            if shared_link.is_symlink():
                shared_link.unlink()
            elif shared_link.exists():
                print(f"⚠️  {shared_link} exists but is not a symlink, skipping")
                continue
            
            try:
                shared_link.symlink_to(shared_source)
                print(f"✅ Created shared symlink for {service['name']}")
            except OSError as e:
                print(f"❌ Failed to create symlink for {service['name']}: {e}")
    
    def start_service(self, service_config):
        """Start a single service"""
        name = service_config["name"]
        directory = service_config["directory"]
        command = service_config["command"]
        port = service_config["port"]
        
        if not Path(directory).exists():
            print(f"❌ Service directory {directory} does not exist")
            return False
        
        print(f"🚀 Starting {name} on port {port}...")
        
        try:
            process = subprocess.Popen(
                command,
                cwd=directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[name] = {
                "process": process,
                "config": service_config
            }
            
            print(f"✅ Started {name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def stop_service(self, name):
        """Stop a single service"""
        if name not in self.processes:
            return
        
        print(f"🛑 Stopping {name}...")
        process = self.processes[name]["process"]
        
        try:
            process.terminate()
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print(f"⚠️  Force killing {name}...")
            process.kill()
            process.wait()
        
        del self.processes[name]
        print(f"✅ Stopped {name}")
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for name in list(self.processes.keys()):
            self.stop_service(name)
        
        self.running = False
    
    def check_service_health(self, name, port):
        """Check if service is responding"""
        try:
            import urllib.request
            response = urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2)
            return response.getcode() == 200
        except:
            return False
    
    def monitor_services(self):
        """Monitor running services"""
        while self.running:
            print(f"\n📊 Service Status ({time.strftime('%H:%M:%S')})")
            print("-" * 50)
            
            for name, service_info in self.processes.items():
                process = service_info["process"]
                config = service_info["config"]
                port = config["port"]
                
                # Check if process is still running
                if process.poll() is not None:
                    print(f"❌ {name:20} | CRASHED (exit code: {process.returncode})")
                    continue
                
                # Check health endpoint
                healthy = self.check_service_health(name, port)
                status = "HEALTHY" if healthy else "STARTING"
                icon = "✅" if healthy else "🔄"
                
                print(f"{icon} {name:20} | {status:10} | PID: {process.pid:6} | Port: {port}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def run_all_services(self):
        """Run all services"""
        print("🎯 Charlie Reporting - Development Service Runner")
        print("=" * 50)
        
        # Setup shared components
        self.setup_shared_components()
        
        # Start all services
        started_services = []
        for service in SERVICES:
            if self.start_service(service):
                started_services.append(service["name"])
            time.sleep(2)  # Stagger startup
        
        if not started_services:
            print("❌ No services started successfully")
            return
        
        print(f"\n🎉 Started {len(started_services)} services:")
        for name in started_services:
            service = next(s for s in SERVICES if s["name"] == name)
            print(f"   • {name} - http://localhost:{service['port']}")
        
        print("\n📝 Useful URLs:")
        print("   • Health checks: http://localhost:PORT/health")
        print("   • Metrics: http://localhost:PORT/metrics")
        print("   • API docs: http://localhost:PORT/docs")
        
        print("\n💡 Press Ctrl+C to stop all services")
        
        # Start monitoring
        self.running = True
        try:
            self.monitor_services()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all_services()


def main():
    """Main entry point"""
    runner = ServiceRunner()
    
    # Handle signals for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        runner.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        runner.run_all_services()
    except Exception as e:
        print(f"❌ Error: {e}")
        runner.stop_all_services()
        sys.exit(1)


if __name__ == "__main__":
    main()

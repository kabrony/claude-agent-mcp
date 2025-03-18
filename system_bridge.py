"""
System Bridge - Cross-platform command execution and system management
"""
import platform
import os
import json
import asyncio
import subprocess

class SystemBridge:
    def __init__(self):
        self.platform = platform.system()
        self.remote_connections = {}
        
    async def execute_local(self, command):
        """Execute a command on the local system"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "code": process.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def connect_remote(self, system_type, host, username, password=None, key_file=None):
        """Connect to a remote system"""
        if system_type.lower() == "ubuntu":
            try:
                # Try to import paramiko, install if not available
                try:
                    import paramiko
                except ImportError:
                    print("Installing paramiko for SSH connections...")
                    subprocess.call(["pip", "install", "paramiko"])
                    import paramiko
                
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                if key_file:
                    client.connect(host, username=username, key_filename=key_file)
                else:
                    client.connect(host, username=username, password=password)
                    
                self.remote_connections["ubuntu"] = client
                return {"success": True, "message": f"Connected to {host} as {username}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
                
    async def execute_remote(self, system_key, command):
        """Execute a command on a remote system"""
        if system_key not in self.remote_connections:
            return {"success": False, "error": f"No connection to {system_key}"}
            
        try:
            client = self.remote_connections[system_key]
            stdin, stdout, stderr = client.exec_command(command)
            
            return {
                "success": stdout.channel.recv_exit_status() == 0,
                "stdout": stdout.read().decode(),
                "stderr": stderr.read().decode(),
                "code": stdout.channel.recv_exit_status()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_system_info(self):
        """Get information about the current system"""
        info = {
            "platform": self.platform,
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "connections": list(self.remote_connections.keys())
        }
        return info

import os
import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success: {command}")
    else:
        print(f"❌ Error: {command}\n{result.stderr}")

def setup_vcan():
    print("Disabling can0...")
    run_command("sudo ip link set can0 down")
    
    print("Loading vcan module...")
    run_command("sudo modprobe vcan")
    
    print("Creating vcan0 interface...")
    run_command("sudo ip link add dev vcan0 type vcan")
    
    print("Bringing up vcan0...")
    run_command("sudo ip link set vcan0 up")
    
    print("Verifying vcan0...")
    run_command("ip link show type vcan")

if __name__ == "__main__":
    setup_vcan()

import subprocess
import json

output_file = "trusted_devices.json"

def create_devices_list():
    """Fetches Bluetooth devices and saves them as a JSON array."""
    try:
        result = subprocess.run(
            ["bluetoothctl", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode != 0:
            print("❌ Error running bluetoothctl. Make sure Bluetooth is enabled.")
            return

        devices = result.stdout.strip().split("\n")

        device_list = []
        for device in devices:
            parts = device.split(maxsplit=2)  # Example: ["Device", "98:B8:BC:36:80:EF", "Andy's Galaxy S20 FE"]
            if len(parts) >= 3:
                mac_address = parts[1]  # Extract MAC address
                name = parts[2]         # Extract device name
                device_list.append({"name": name, "mac_address": mac_address})

        if device_list:
            with open(output_file, "w") as f:
                json.dump(device_list, f, indent=4)  # Save as formatted JSON
            print(f"✅ Devices saved to {output_file}")
        else:
            print("⚠️ No Bluetooth devices found.")

    except Exception as e:
        print(f"❌ Error: {e}")

def load_devices(file_path="trusted_devices.json"):
    """Loads Bluetooth devices from JSON and returns a list, or None if empty."""
    try:
        with open(file_path, "r") as f:
            devices = json.load(f)
            return devices if devices else None
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    
if __name__ == "__main__":
    create_devices_list()

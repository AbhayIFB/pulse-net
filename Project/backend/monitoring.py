# Import the network discovery function
from network import discover_devices

# Store the most recent network scan
current_devices = []

# Store the previous network scan
previous_devices = []

# Store persistent information about devices across scans
device_state = {}

# Number of consecutive missed scans before a device is considered offline
MAX_MISSED_SCANS = 2


# Get the current devices on the network
def get_current_devices():

    global current_devices
    global previous_devices
    global device_state

    # Preserve the previous scan
    previous_devices = current_devices

    # Perform a new network scan
    scanned_devices = discover_devices()

    # Keep track of which IPs responded to this scan
    seen_ips = set()

    # Update the state of devices that were discovered
    for device in scanned_devices:

        ip = device["ip"]
        seen_ips.add(ip)

        # If this is a new device, create its state
        if ip not in device_state:
            device_state[ip] = {
                **device,
                "missed_scans": 0
            }

        else:
            # Update the device's latest information
            device_state[ip].update(device)

            # Reset missed scans because we found it again
            device_state[ip]["missed_scans"] = 0

    # Check devices that were NOT found in this scan
    for ip, device in device_state.items():

        if ip not in seen_ips:

            # Increase the consecutive missed-scan counter
            device["missed_scans"] += 1

            # Consider the device offline after enough missed scans
            if device["missed_scans"] >= MAX_MISSED_SCANS:
                device["status"] = "offline"
                device["latency_ms"] = None

    # Convert our state dictionary back into a list
    current_devices = list(device_state.values())

    return current_devices



# Detect changes between the previous and current network scans
def detect_changes():

    # Extract IP addresses from the previous scan
    previous_ips = {device["ip"] for device in previous_devices}

    # Extract IP addresses from the current scan
    current_ips = {device["ip"] for device in current_devices}

    # Devices present now but not in the previous scan
    new_devices = current_ips - previous_ips

    # Devices present previously but missing from the current scan
    removed_devices = previous_ips - current_ips

    return {
        "new_devices": list(new_devices),
        "removed_devices": list(removed_devices)
    }
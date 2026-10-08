# Import the network discovery function
from network import discover_devices

# Store the most recent network scan
current_devices = []

# Store the previous network scan
previous_devices = []

# Store persistent information about devices across scans
device_state = {}

# Track whether Pulse Net has completed its first monitoring cycle
has_previous_scan = False

# Number of consecutive missed scans before a device is considered offline
MAX_MISSED_SCANS = 2



# Run one complete monitoring cycle
def run_monitoring_cycle():

    # # Allow this function to modify the module-level scan state
    global has_previous_scan

    # Discover devices and update their current state
    devices = get_current_devices()

    # Store anomaly results for devices
    anomalies = []

    # Detect changes based on if previous_scan exists or not
    if not has_previous_scan:
        changes = {
            "new_devices": [],
            "removed_devices": []
        }

        has_previous_scan = True

    else:
        changes = detect_changes()

    # Analyze each device for latency anomalies
    for device in devices:

        result = detect_latency_anomaly(device["ip"])

        # Add the device if an anomaly was detected
        if result and result["anomaly"]:
            anomalies.append({
                "ip": device["ip"],
                **result
            })

    # Return the results of this monitoring cycle
    return {
        "devices": devices,
        "changes": changes,
        "anomalies": anomalies
    }



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
                "missed_scans": 0,
                "latency_history": []
            }

        else:
            # Update the device's latest information
            device_state[ip].update(device)

            # Reset missed scans because we found it again
            device_state[ip]["missed_scans"] = 0

        # Store the latest latency measurement in the device's history
        if device["latency_ms"] is not None:

            device_state[ip]["latency_history"].append(
                device["latency_ms"]
            )

            # Keep only the 10 most recent measurements
            device_state[ip]["latency_history"] = (
                device_state[ip]["latency_history"][-10:]
            )

    # Check devices that were NOT found in this scan
    for ip, device in device_state.items():

        if ip not in seen_ips:

            # Increase the consecutive missed-scan counter
            device["missed_scans"] += 1

            # Consider the device offline after enough missed scans
            if device["missed_scans"] >= MAX_MISSED_SCANS:
                device["status"] = "offline"
                device["latency_ms"] = None

    # Save the current scan in the current devices
    current_devices = scanned_devices

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



# Calculate latency statistics for a device
def get_latency_stats(ip):

    # Check whether the device exists
    if ip not in device_state:
        return None

    # Get the device's latency history
    history = device_state[ip]["latency_history"]

    # There is no latency data to analyze
    if not history:
        return None

    return {
        "average_ms": round(sum(history) / len(history), 2),
        "minimum_ms": round(min(history), 2),
        "maximum_ms": round(max(history), 2)
    }



# Detect whether a device's latest latency is unusually high
def detect_latency_anomaly(ip):

    # Check whether the device exists
    if ip not in device_state:
        return None

    # Get the device's latency history
    history = device_state[ip]["latency_history"]

    # We need enough previous measurements to establish a baseline
    if len(history) < 6:
        return {
            "anomaly": False,
            "reason": "Not enough historical data"
        }

    # The latest measurement is what we want to evaluate
    current_latency = history[-1]

    # Use the measurements before the current one as the baseline: in this case we are reading atleast 5 measurements
    baseline_history = history[:-1]

    # Calculate the average historical latency
    baseline_average = sum(baseline_history) / len(baseline_history)

    # Calculate how much higher the current latency is
    latency_increase = current_latency - baseline_average

    # Create a boolean to determine whether the current latency is anomalous
    is_anomaly = (
        current_latency >= baseline_average * 2
        and latency_increase >= 10
    )

    # Create an explanation for the result
    if is_anomaly:
        reason = "Latency is significantly above the device baseline"
    else:
        reason = "Latency is within the expected range"

    return {
        "anomaly": is_anomaly,
        "reason": reason,
        "current_latency_ms": round(current_latency, 2),
        "baseline_average_ms": round(baseline_average, 2)
    }
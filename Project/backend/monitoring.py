# Import the network discovery function
from network import discover_devices


# Get the current devices on the network
def get_current_devices():

    # Run a network scan and discover the devices currently responding
    devices = discover_devices()

    # Return the discovered devices
    return devices
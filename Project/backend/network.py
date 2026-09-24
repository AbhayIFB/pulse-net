# Importing the required Python libraries
import ipaddress
import socket
import psutil

# Import the networking tools we need from Scapy
from scapy.all import Ether, ARP, srp



def get_local_network():
    # Create a UDP socket so the operating system can tell us which local IP address is used for the active network connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to an external address without sending application data
        sock.connect(("8.8.8.8", 80))

        # Get the local IP address selected by the operating system
        local_ip = sock.getsockname()[0]

    finally:
        # Close the socket when we're finished
        sock.close()

    # Get information about all network interfaces
    interfaces = psutil.net_if_addrs()

    # Look through each network interface
    for interface_name, addresses in interfaces.items():

        # Look through the addresses assigned to this interface
        for address in addresses:

            # Find the IPv4 address that matches our active local IP
            if address.family == socket.AF_INET and address.address == local_ip:

                # Get the subnet mask assigned to that interface
                netmask = address.netmask

                # Calculate the network using the IP and subnet mask
                network = ipaddress.ip_network(
                    f"{local_ip}/{netmask}",
                    strict=False
                )

                # Return the network in CIDR notation
                return network

    # If no matching interface was found, raise an error
    raise RuntimeError("Could not determine the local network")




# Discover Devices connected to the local network using ARP
def discover_devices():
    # Determine the local network automatically
    network = get_local_network()
    
    # Create an Ethernet broadcast frame containing an ARP request for every address in the local network
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(
        pdst=str(network)
    )

    # Send the ARP requests and wait up to 2 seconds for responses
    # 'answered' contains devices that responded
    # 'unanswered' contains requests that received no response
    answered, unanswered = srp(
        packet,
        timeout=2,
        verbose=0
    )

    # Create an empty list to store the devices we discover
    devices = []

    # Go through every device that responded to our ARP requests
    for sent, received in answered:

        # Store the device's IP address and MAC address
        device = {
            "ip": received.psrc,
            "mac": received.hwsrc
        }

        # Add the device to our list
        devices.append(device)

    # Return the list of discovered devices
    return devices

# Only run the following code when this file is executed directly and not when discover_devices() is imported into another Python file
if __name__ == "__main__":

    # Run the network discovery function
    devices = discover_devices()

    # Print each discovered device
    for device in devices:
        print(device)
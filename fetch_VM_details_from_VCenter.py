import ssl
import argparse
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def get_vm_by_name(content, vm_name):
    """
    Search for a VM by its name.
    """
    obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_list = obj_view.view
    obj_view.Destroy()
    for vm in vm_list:
        if vm.name == vm_name:
            return vm
    return None

def connect_to_vcenter(server, user, password):
    """
    Connect to a vCenter server and return the service instance and content.
    """
    context = ssl._create_unverified_context()
    si = SmartConnect(host=server, user=user, pwd=password, sslContext=context)
    content = si.RetrieveContent()
    return si, content

def main():
    # Hardcoded user and password details
    user = "your-username"
    password = "your-password"

    # List of vCenter servers
    vcenters = [
        "vcenter1.example.com",
        "vcenter2.example.com",
        # Add more vCenter details as needed
    ]

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Get VM details from vCenter servers.')
    parser.add_argument('vm_name', type=str, help='Name of the virtual machine')
    args = parser.parse_args()

    vm_name = args.vm_name
    vm_found = False
    for vcenter in vcenters:
        try:
            si, content = connect_to_vcenter(vcenter, user, password)
            vm = get_vm_by_name(content, vm_name)
            if vm:
                print(f"VM found on {vcenter}")
                print(f"Name: {vm.name}")
                print(f"Power State: {vm.runtime.powerState}")
                print(f"CPU Count: {vm.config.hardware.numCPU}")
                print(f"Memory (MB): {vm.config.hardware.memoryMB}")
                print(f"Guest OS: {vm.config.guestFullName}")
                print(f"IP Address: {vm.guest.ipAddress}")
                print(f"Host: {vm.runtime.host.name}")
                vm_found = True
                Disconnect(si)
                break
            Disconnect(si)
        except vim.fault.NoPermission as e:
            print(f"Permission error connecting to {vcenter}: {e}")
        except Exception as e:
            print(f"Error connecting to {vcenter}: {e}")
    
    if not vm_found:
        print(f"VM '{vm_name}' not found on any vCenter.")

if __name__ == "__main__":
    main()

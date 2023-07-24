import os
import time
import shutil
import subprocess
import serial.tools.list_ports

def check_rshell_availability():
    try:
        result = subprocess.run(['rshell', 'ls'], capture_output=True, text=True, check=True)
        #print(result.stdout)
        if "No MicroPython boards connected" in result.stdout:
            return False
        return True
    except subprocess.CalledProcessError as e:
        return False

def find_mounted_drive(drive_name):
    mounted_drives = [d for d in os.listdir('/Volumes') if not d.startswith('.')]
    for drive in mounted_drives:
        if drive_name in drive:
            return os.path.join('/Volumes', drive)
    return None

def copy_uf2_to_drive(uf2_file, drive_name):
    mounted_drive = find_mounted_drive(drive_name)
    if mounted_drive:
        try:
            destination_file = os.path.join(mounted_drive, os.path.basename(uf2_file))
            shutil.copy(uf2_file, destination_file)
            return True
        except Exception as e:
            print(f"Error copying .uf2 file: {e}")
            return False
    else:
        print(f"Drive '{drive_name}' not found.")
        return False

def sync_filesystem():
    try:
        subprocess.run(['rshell', 'rsync', '-a', 'firmware/', '/pyboard'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error syncing filesystem: {e}")
        return False

def wait_for_pico():
    rshell_available = False
    while True:
        print("Waiting for Raspberry Pi Pico to be connected...")

        # Check if rshell is available
        if not check_rshell_availability():
            # Copy the .uf2 file to the mounted drive
            uf2_file = 'microPython-pico.uf2'
            drive_name = 'RPI-RP2'
            if copy_uf2_to_drive(uf2_file, drive_name):
                print(f"{uf2_file} copied to {drive_name}.")
            else:
                print("Failed to copy .uf2 file.")
                continue

            # Wait a few seconds after copying
            time.sleep(5)

        # Sync the filesystem using rshell and rsync
        else:
            rshell_available = True
            if sync_filesystem():
                print("Sync completed successfully.")
            else:
                print("Failed to sync filesystem.")
            
            # Prompt user to press any key to continue
            input("Press any key to continue...")
            
        time.sleep(2)

if __name__ == "__main__":
    wait_for_pico()

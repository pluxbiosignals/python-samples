import platform
import sys

system = platform.system()
machine = platform.machine().lower()
architecture = platform.architecture()[0][:2]
major, minor = platform.python_version().split(".")[:2]

try:
    if system == "Windows":
        if (int(major), int(minor)) < (3, 7):
            raise ValueError("3.7")
        api_dir = f"Win{architecture}_{major}{min(13, int(minor))}"
    if system == "Darwin":
        if machine == "x86_64":
            if (int(major), int(minor)) < (3, 7):
                raise ValueError("3.7")
            api_dir = f"MacOS/Intel{major}{min(10, int(minor))}"
        if machine == "arm64":
            if (int(major), int(minor)) < (3, 7):
                raise ValueError("3.7")
            api_dir = f"M1_{major}{min(12, int(minor))}"
    if system == "Linux":
        if machine.startswith("arm") and architecture == "32":
            if (int(major), int(minor)) < (3, 11):
                api_dir = f"LinuxARM32"
            else:
                api_dir = f"LinuxARM32_311"
        elif (machine.startswith("arm") and architecture == "64") or machine.startswith(
            "aarch64"
        ):
            if (int(major), int(minor)) < (3, 8):
                raise ValueError("3.8")
            api_dir = f"LinuxARM64_{major}{min(9, int(minor))}"
        elif architecture == "64":
            api_dir = f"Linux64"

    api_dir = f"PLUX-API-Python3/{api_dir}"  # Change here for manual specification.
    sys.path.append(api_dir)
    print(f"Loaded API: {api_dir}")
except ValueError as e:
    print(f"Python version required is ≥ {e}. Installed is {platform.python_version()}")
    sys.exit(1)


import plux
import datetime

class NewDevice(plux.MemoryDev):
    def __init__(self, address):
        plux.MemoryDev.__init__(address)

    def onSessionRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        if nSeq % 2000 == 0:
            print(nSeq, *data)


# example routines


def exampleDownloadAcquisition(
    address="BTH00:07:80:4D:2E:76",
):
    """
    Example of the actions needed to download a data recording that was stored in the Device Memory Card.
    """
    device = NewDevice(address)

    # Retrieve the list of Sessions stored in the Memory Card.
    list_of_sessions = device.getSessions()
    
    # Start downloading the last one.
    device.replaySession(list_of_sessions[-1].startTime)
    
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleDownloadAcquisition(*sys.argv[1:])

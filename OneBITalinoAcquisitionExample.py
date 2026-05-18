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

class NewDevice(plux.SignalsDev):
    def __init__(self, address):
        plux.SignalsDev.__init__(address)
        self.duration = 0
        self.frequency = 0

    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        if nSeq % 2000 == 0:
            print(nSeq, *data)
        return nSeq > self.duration * self.frequency


# example routines


def exampleAcquisition(
    address="BTH00:07:80:4D:2E:76",
    duration=20,
    frequency=1000,
    active_ports=[1, 2, 3, 4, 5, 6],
):  # time acquisition for each frequency
    """
    Example acquisition.
    """
    device = NewDevice(address)
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.
    
    # Trigger the start of the data recording: https://www.downloads.plux.info/apis/PLUX-API-Python-Docs/classplux_1_1_signals_dev.html#a028eaf160a20a53b3302d1abd95ae9f1
    device.start(device.frequency, active_ports, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleAcquisition(*sys.argv[1:])

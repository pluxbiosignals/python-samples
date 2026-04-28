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
        self.duration = 0
        self.frequency = 0

    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        if nSeq % 2000 == 0:
            print(nSeq, *data)
        return nSeq > self.duration * self.frequency


# example routines


def exampleAcquisition(
    address="BTH00:07:80:4D:2E:76",
    start_in_seconds=30,
    duration=20,
    frequency=1000,
):
    """
    Example of scheduling a future acquisition to be stored in the memory card.
    """
    device = NewDevice(address)
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.
    
    # Create a Source for each Channel that will have a sensor attached during the future data recording.
    # >>> Port 3
    source_port_3 = plux.Source()
    source_port_3.port = 3
    source_port_3.nBits = 16 # ADC Resolution in bits.
    source_port_3.chMask = 0x01 # Channel Mask: 0x01 for Analog sensors connected in Port 1-8 and 0x03 for Digital Sensors like SpO2 and fNIRS connected to the bottom-left port of the hub (down arrow).
    # >>> Port 5
    source_port_5 = plux.Source()
    source_port_5.port = 5
    source_port_5.nBits = 16 # ADC Resolution in bits.
    source_port_5.chMask = 0x01 # Channel Mask: 0x01 for Analog sensors connected in Port 1-8 and 0x03 for Digital Sensors like SpO2 and fNIRS connected to the bottom-left port of the hub (down arrow).
    
    # Definition of the Schedule configuration.
    schedule = plux.Schedule()
    schedule.startTime = datetime.datetime.now() + datetime.timedelta(seconds=start_in_seconds) # Start the data recording in start_in_seconds seconds.
    schedule.duration = duration # in seconds
    schedule.baseFreq = frequency
    schedule.sources = [source_port_3, source_port_5]
    
    # Program the Schedule in the Device.
    device.addSchedule(schedule)
    
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleAcquisition(*sys.argv[1:])

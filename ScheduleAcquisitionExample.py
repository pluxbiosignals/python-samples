import platform
import sys

osDic = {
    "Darwin": f"MacOS/Intel{''.join(platform.python_version().split('.')[:2])}",
    "Linux": "Linux64",
    "Windows": f"Win{platform.architecture()[0][:2]}_{''.join(platform.python_version().split('.')[:2])}",
}
if platform.mac_ver()[0] != "":
    import subprocess
    from os import linesep

    p = subprocess.Popen("sw_vers", stdout=subprocess.PIPE)
    result = p.communicate()[0].decode("utf-8").split(str("\t"))[2].split(linesep)[0]
    if result.startswith("12."):
        print("macOS version is Monterrey!")
        osDic["Darwin"] = "MacOS/Intel310"
        if (
            int(platform.python_version().split(".")[0]) <= 3
            and int(platform.python_version().split(".")[1]) < 10
        ):
            print(f"Python version required is ≥ 3.10. Installed is {platform.python_version()}")
            exit()


sys.path.append(f"PLUX-API-Python3/{osDic[platform.system()]}")

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

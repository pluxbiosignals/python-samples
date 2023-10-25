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


class NewDevice(plux.SignalsDev):
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
    address="BTH00:07:80:D8:AA:AD",
    duration=20,
    frequency=1000,
):  # time acquisition for each frequency
    """
    Example acquisition using the plux.Source object to initialize specific channels of the biosignalsplux hub.

    In this example, it will be demonstrated how-to initialize an Analog Channel (valid ports 1-8) and a Digital Channel (valid port 9).
    """
    device = NewDevice(address)
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.
    
    # Configure the channels that will be collecting data during the real-time data acquisition.
    # >>> Analog Channel (CH3).
    analog_source_ch3 = plux.Source()
    analog_source_ch3.port = 3
    analog_source_ch3.freqDivisor = 1 # The subsampling factor that will be applied to this channel 
                                      # (1 --> No subsampling applied, 2 --> the sampling rate for the current channel
                                      # will be half of the specified device.frequency, 3 --> ...).
    analog_source_ch3.nBits = 16 # The resolution(in bits) used by the Analog-to-Digital Converter (ADC) module in this port.
    analog_source_ch3.chMask = 0x01 # The number of derivations that this channel will have (Analog Channels will always have a single derivation, i.e., 
                                    # will only produce a signal).
                                    
    # >>> Digital Channel (CH9).
    digital_source_ch9 = plux.Source()
    digital_source_ch9.port = 9
    digital_source_ch9.freqDivisor = 1 # The subsampling factor that will be applied to this channel 
                                      # (1 --> No subsampling applied, 2 --> the sampling rate for the current channel
                                      # will be half of the specified device.frequency, 3 --> ...).
    digital_source_ch9.nBits = 16 # The resolution(in bits) used by the Analog-to-Digital Converter (ADC) module in this port.
    digital_source_ch9.chMask = 0x03 # The number of derivations that this channel will have (A Digital Channels linked to a SpO2 or fNIRS sensor 
                                     # will have two derivations, i.e., it will produce two signals (RED and INFRARED).
                                     # The activation of the two derivation is made with the 0x03 hexadecimal code which corresponds to the 11 binary representation
                                     # stating that derivation 1/RED - represented by the Least Significant Bit (LSb) - and the derivation 2/INFRARED - represented by the 
                                     # Most Significant Bit (MSb) - should be active).
    
    device.start(device.frequency, [analog_source_ch3, digital_source_ch9])
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleAcquisition(*sys.argv[1:])

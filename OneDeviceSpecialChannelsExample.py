from pathlib import Path
import platform
import sys


API_BASE_DIR = "PLUX-API-Python3"
API_BASE_PATH = Path(__file__).resolve().parent / API_BASE_DIR


def _python_version():
    """Return the Python major and minor version as integers."""
    major, minor = platform.python_version_tuple()[:2]
    return int(major), int(minor)


def _is_arm_64(machine, architecture):
    """Return whether the current machine should be treated as ARM 64-bit."""
    return machine.startswith("aarch64") or (
        machine.startswith("arm") and architecture == "64"
    )


def _available_api_dirs(api_base_path):
    """Return the available API directories for diagnostic purposes."""
    if not api_base_path.is_dir():
        return []

    return sorted(path.name for path in api_base_path.iterdir() if path.is_dir())


def _first_existing_api_dir(candidates):
    """Return the first candidate API directory that exists."""
    for candidate in candidates:
        if (API_BASE_PATH / candidate).is_dir():
            return candidate

    raise ValueError(
        "Unsupported platform/Python combination: "
        f"system={platform.system()}, machine={platform.machine().lower()}, "
        f"architecture={platform.architecture()[0][:2]}, "
        f"python={platform.python_version()}, "
        f"attempted_api_dirs={', '.join(candidates)}, "
        f"available_api_dirs={', '.join(_available_api_dirs(API_BASE_PATH)) or 'none'}"
    )


def _resolve_api_dir():
    """Resolve the PLUX API directory for the current platform."""
    system = platform.system()
    machine = platform.machine().lower()
    architecture = platform.architecture()[0][:2]
    major, minor = _python_version()

    if not API_BASE_PATH.is_dir():
        raise ValueError(f"API base directory does not exist: {API_BASE_PATH}")

    if major != 3:
        raise ValueError(
            f"Unsupported Python major version: {platform.python_version()}. "
            "Python 3 is required."
        )

    version_suffix = f"{major}{minor}"

    if system == "Windows":
        return _first_existing_api_dir([f"Win{architecture}_{version_suffix}"])

    if system == "Darwin":
        if machine == "x86_64":
            return _first_existing_api_dir(
                [f"MacOS/Intel{version_suffix}", "MacOS"]
            )

        if machine == "arm64":
            return _first_existing_api_dir([f"M1_{version_suffix}"])

        raise ValueError(f"Unsupported macOS architecture: {machine}")

    if system == "Linux":
        if machine.startswith("arm") and architecture == "32":
            candidates = [f"LinuxARM32_{version_suffix}"]

            if minor < 11:
                candidates.append("LinuxARM32")

            return _first_existing_api_dir(candidates)

        if _is_arm_64(machine, architecture):
            return _first_existing_api_dir([f"LinuxARM64_{version_suffix}"])

        if architecture == "64":
            return _first_existing_api_dir([f"Linux64_{version_suffix}", "Linux64"])

        raise ValueError(
            f"Unsupported Linux architecture: machine={machine}, "
            f"architecture={architecture}"
        )

    raise ValueError(f"Unsupported operating system: {system}")


try:
    api_dir = _resolve_api_dir()
    api_path = API_BASE_PATH / api_dir

    sys.path.append(str(api_path))
    print(f"Loaded API: {api_path}")

except ValueError as error:
    print(error)
    sys.exit(1)


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

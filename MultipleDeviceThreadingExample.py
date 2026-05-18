from pathlib import Path
import platform
import sys
import threading


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
        self.time = 0
        self.frequency = 0

    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        if nSeq % 2000 == 0:
            print(nSeq)
        if nSeq / self.frequency > self.time:
            return True
        return False


# example routines


def exampleAcquisition(address, time, freq, code):  # time acquisition for each frequency
    """
    Example acquisition.

    Supported channel number codes:
    {1 channel - 0x01, 2 channels - 0x03, 3 channels - 0x07
    4 channels - 0x0F, 5 channels - 0x1F, 6 channels - 0x3F
    7 channels - 0x7F, 8 channels - 0xFF}

    Maximum acquisition frequencies for number of channels:
    1 channel - 8000, 2 channels - 5000, 3 channels - 4000
    4 channels - 3000, 5 channels - 3000, 6 channels - 2000
    7 channels - 2000, 8 channels - 2000
    """
    device = NewDevice(address)
    device.time = time  # interval of acquisition
    device.frequency = freq
    device.start(device.frequency, code, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


def createThreads(address_list, time, freq_list, code_list):
    thread_list = []
    for index in range(len(address_list)):
        thread_list.append(
            threading.Thread(
                target=exampleAcquisition,
                args=(
                    address_list[index],
                    time,
                    freq_list[index],
                    code_list[index],
                ),
            )
        )
        thread_list[index].start()
    for index in range(len(address_list)):
        thread_list[index].join()
    if platform.system() == "Darwin":
        plux.MacOS.stopMainLoop()


def createMainThread(address_list, time, freq_list, code_list):

    main_thread = threading.Thread(
        target=createThreads, args=(address_list, time, freq_list, code_list)
    )
    main_thread.start()
    if platform.system() == "Darwin":
        plux.MacOS.runMainLoop()
    main_thread.join()


createMainThread(
    ["BTH00:07:80:D8:AB:46", "BTH00:07:80:3B:46:58", "BTH00:07:80:4D:2E:76"],
    20,
    [1000, 1000, 1000],
    [0xFF, 0xFF, 0x01],
)

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

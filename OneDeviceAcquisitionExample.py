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
        elif (machine.startswith("arm") and architecture == "64") or machine.startswith("aarch64"):
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
        self.duration = 0
        self.frequency = 0

    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments
        if nSeq % 2000 == 0:
            print(nSeq, *data)
        return nSeq > self.duration * self.frequency

    def getConnectedSensors(self):
        sensors = self.getSensors()

        # Map values to sensor labels
        SENSOR_CLASS = {
            0: 'UNKNOWN', 1: 'EMG', 2: 'ECG', 3: 'LIGHT', 4: 'EDA', 5: 'BVP',
            6: 'RESP', 7: 'XYZ', 8: 'SYNC', 9: 'EEG', 10: 'SYNC_ADAP', 11: 'SYNC_LED',
            12: 'SYNC_SW', 13: 'USB', 14: 'FORCE', 15: 'TEMP', 16: 'VPROBE',
            17: 'BREAKOUT', 18: 'OXIMETER', 19: 'GONI', 20: 'ACT', 21: 'EOG',
            22: 'EGG', 23: 'ANSA', 26: 'OSL'
        }

        # Map values to color labels
        SENSOR_COLOR = {
            0: 'UNKNOWN', 1: 'BLACK', 2: 'GRAY', 3: 'WHITE', 4: 'DARKBLUE',
            5: 'LIGHTBLUE', 6: 'RED', 7: 'GREEN', 8: 'YELLOW', 9: 'ORANGE'
        }

        port_mask = 0  # This is your dynamic bitmask

        print("Connected sensors:")
        for port, sensor in sensors.items():
            print(f"\nSensor on port {port}:")
            print(f"  Type/Class: {SENSOR_CLASS.get(sensor.clas, 'Unknown')} ({sensor.clas})")
            print(f"  Serial #: {sensor.serialNum}")
            print(f"  Color: {SENSOR_COLOR.get(sensor.color, 'Unknown')} ({sensor.color})")
            # Build bitmask: bit position = port - 1
            port_mask |= (1 << (port - 1))

        return port_mask


# example routines


def exampleAcquisition(
    address="BTH00:07:80:4D:2E:76",
    duration=20,
    frequency=1000,
    code=0x01,
):  # time acquisition for each frequency
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
    device.duration = int(duration)  # Duration of acquisition in seconds.
    device.frequency = int(frequency)  # Samples per second.

    # Get Battery level
    battery = device.getBattery()
    print(f"\nBattery charging level at {int(battery)}%")

    # Get port mask based on connected sensors
    sensors = device.getConnectedSensors()

    if isinstance(code, str):
        code = int(code, 16)  # From hexadecimal str to int
    device.start(device.frequency, code, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


if __name__ == "__main__":
    # Use arguments from the terminal (if any) as the first arguments and use the remaining default values.
    exampleAcquisition(*sys.argv[1:])

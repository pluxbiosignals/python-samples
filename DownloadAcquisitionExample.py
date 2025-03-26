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

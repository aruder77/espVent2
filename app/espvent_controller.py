from esp_micro.esp_micro_controller import EspMicroController
from espvent_device import EspVentDevice


class EspVentController(EspMicroController):
    def __init__(self):
        super().__init__()

    def createHomieDevice(self, settings):
        return EspVentDevice(settings)

    def getDeviceName(self):
        return 'espVentuPy'

    def getDeviceID(self):
        return 'espVentuPy'

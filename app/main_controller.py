from app.espvent_display import EspVentDisplay
from esp_micro.esp_micro_controller import EspMicroController
from espvent_device import EspVentDevice
from espvent_display import EspVentDisplay


class MainController(EspMicroController):
    def __init__(self):
        super().__init__()
        EspVentDisplay()

    def createHomieDevice(self, settings):
        return EspVentDevice(settings)

    def getDeviceName(self):
        return 'espVentuMicro'

    def getDeviceID(self):
        return 'espVentuMicro'

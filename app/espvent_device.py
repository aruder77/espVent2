from app.MotorsNode import MotorsNode
from homie.device import HomieDevice, await_ready_state
from utime import time
from MotorNode import MotorNode


class EspVentDevice(HomieDevice):

    def __init__(self, settings):
        super().__init__(settings)

        motorNodes = [
            MotorNode(33, 1, False), 
            MotorNode(32, 2, True),
            MotorNode(17, 3, False),
            MotorNode(16, 4, True),
            MotorNode(13, 5, False),
            MotorNode(27, 6, True), 
            MotorNode(26, 7, False), 
            MotorNode(25, 8, True) 
        ]
        for motorNode in motorNodes:
            self.add_node(motorNode)

        self.add_node(MotorsNode(motorNodes))
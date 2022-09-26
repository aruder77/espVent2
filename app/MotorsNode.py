from homie.constants import FALSE, BOOLEAN, INTEGER
from homie.property import HomieProperty
from homie.node import HomieNode
from homie.device import await_ready_state
import uasyncio as asyncio
from uasyncio import sleep_ms
from gc import collect
import gc



WORKER_DELAY = const(100)

class MotorsNode(HomieNode):

    direction = False
    cycleTime = 75
    directionChangeLoopCount = cycleTime * 1000.0 / 100
    loopCounter = 0
    mode = 0

    def __init__(self, motorNodes):
        super().__init__(id="fans", name="Fans", type="Fan")
        self.motorNodes = motorNodes

        self.speedProperty = HomieProperty(
            id="speed",
            name="speed",
            settable=True,
            datatype=INTEGER,
            unit="%",
            default=50,
            on_message=self.speed_msg,
        )
        self.add_property(self.speedProperty)

        self.directionProperty = HomieProperty(
            id="direction",
            name="direction",
            settable=True,
            datatype=BOOLEAN,
            default=FALSE,
            on_message=self.direction_msg,
        )
        self.add_property(self.directionProperty)

        self.modeProperty = HomieProperty(
            id="mode",
            name="mode",
            settable=True,
            datatype=INTEGER,
            format="0:3",
            default=0,
            on_message=self.mode_msg,
        )
        self.add_property(self.modeProperty)       

        #asyncio.create_task(self.garbageCollection())
        asyncio.create_task(self.workerLoop())        

    async def garbageCollection(self):
        while True:
            collect()
            await sleep_ms(500)
        

    @await_ready_state
    async def workerLoop(self):
        while True: 
            self.loop()

            await sleep_ms(WORKER_DELAY)         


    def speed_msg(self, topic, payload, retained):
        speed = int(payload)
        if speed >= 0 and speed <= 100:
            self.setSpeed(speed)


    def direction_msg(self, topic, payload, retained):
        direction = bool(payload)
        self.setDirection(direction)      


    def mode_msg(self, topic, payload, retained):
        mode = int(payload)
        if mode >= 0 and mode <= 3:
            self.setMode(mode)


    def setSpeed(self, speed: int):
        self.speed = speed

        for motorNode in self.motorNodes:
            motorNode.setTargetSpeed(speed)

        #self.getLogger().info("Speed is %d" % speed)
        self.speedProperty.value = speed


    def setDirection(self, direction: bool):
        if self.mode != 2:
            self.direction = direction
            self.directionProperty.value = "true" if direction else "false"
            #self.getLogger().info("switching direction to %s" % ("out" if direction else "in"))

            for motorNode in self.motorNodes:
                motorNode.setTargetDirection(not direction if motorNode.isInverseDirection() else direction)

    def isDirection(self):
        return self.direction


    def setMode(self, mode: int):
        #self.getLogger().info("Mode: %d" % mode)
        self.mode = mode
        self.modeProperty.value = mode

        if mode == 0 or mode == 1:
            # regular switching mode
            for motorNode in self.motorNodes:
                motorNode.setTargetDirection(not self.direction if motorNode.isInverseDirection() else self.direction)

        elif mode == 2:
            # all in, no inverse direction
            for motorNode in self.motorNodes:
                motorNode.setTargetDirection(False)

        elif mode == 3:
            # manual mode, no inverse direction
            for motorNode in self.motorNodes:
                motorNode.setTargetDirection(self.direction)


    def loop(self):
        if self.loopCounter == self.directionChangeLoopCount:
            # only in mode 0, change direction
            if self.mode == 0:
                self.setDirection(not self.isDirection())

            self.loopCounter = 0

        # adjust all motors speed and direction slowly in every loop
        for motorNode in self.motorNodes:
            motorNode.adjust()

        self.loopCounter += 1

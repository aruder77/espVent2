from homie.constants import FALSE, BOOLEAN, INTEGER
from homie.property import HomieProperty
from homie.node import HomieNode
from machine import Pin, PWM

class MotorNode(HomieNode):

    MAX_PWM = 220
    MIN_PWM = 30
    PWM_RANGE = (MAX_PWM - MIN_PWM) / 2

    CURVE = [ 255,253,253,252,252,252,251,249,247,243,238,233,228,223,218,213,208,203,199,195,192,189,186,184,181,179,177,176,174,173,172,170,168,167,165,164,162,161,160,159,158,158,157,157,156,156,155,154,153,152,151,150,150,149,148,148,147,146,145,145,144,143,142,141,140,140,139,138,138,137,136,135,134,134,133,133,132,131,130,130,129,128,127,127,126,125,124,123,122,121,120,119,118,117,116,114,113,112,110,108,107,105,101,98,95,90,86,82,77,73,69,64,59,54,48,42,36,28,20,14,8,4,2,1,0,0 ]

    currentPwmSignal = 0
    targetPwmSignal = 0
    targetSpeed = 50
    targetDirection = False
    currentIndex = 0

    def __init__(self, pwmPin: int, pwmChannel: int, inverseDirection: bool):
        super().__init__(id="fan%d" % pwmChannel, name="Fan%d" % pwmChannel, type="Fan")
        self.pwm = PWM(Pin(pwmPin), freq=4000)
        self.inverseDirection = inverseDirection

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
            default=False,
            on_message=self.direction_msg,
        )
        self.add_property(self.directionProperty)


    def speed_msg(self, topic, payload, retained):
        print("speed_msg %s" % self.id)
        speed = int(payload)
        if speed >= 0 and speed <= 100:
            self.setTargetSpeed(speed)

    def direction_msg(self, topic, payload, retained):
        print("direction_msg")
        direction = bool(payload)
        self.setTargetDirection(direction)

    def setStartIndex(self, currentValue: int):
        i = 0
        while (self.CURVE[i] >= currentValue and i < 125):
            i += 1

        self.currentIndex = i


    def convertToPwmSignal(self, direction: bool, speed: int):
        pwmSpeed = 0
        realDirection = direction

        pwmDiff = speed/100.0 * self.PWM_RANGE

        if (realDirection):
            pwmSpeed = 125 - pwmDiff
        else:
            pwmSpeed = 125 + pwmDiff

        return pwmSpeed


    def adjust(self):
        if (self.targetPwmSignal > self.currentPwmSignal):
            newValue = self.CURVE[self.currentIndex]
            self.currentIndex = self.currentIndex - 1

            if (newValue > self.targetPwmSignal):
                newValue = self.targetPwmSignal

            self.setCurrentPwmSignal(newValue)

        elif (self.targetPwmSignal < self.currentPwmSignal):
            newValue = self.CURVE[self.currentIndex]
            self.currentIndex = self.currentIndex + 1
            if (newValue < self.targetPwmSignal):
                newValue = self.targetPwmSignal

            self.setCurrentPwmSignal(newValue)
            

    def isInverseDirection(self):
        return self.inverseDirection

    def setInverseDirection(self, inverseDirection: bool):
        self.inverseDirection = inverseDirection

    def getTargetSpeed(self):
        return self.targetSpeed

    def setTargetSpeed(self, targetSpeed: int):
        self.targetSpeed = targetSpeed
        self.targetPwmSignal = self.convertToPwmSignal(self.targetDirection, self.targetSpeed)
        self.setStartIndex(self.currentPwmSignal)
        #self.getLogger().info("new speed: %d, new target pwm: %d" % (self.targetSpeed, self.targetPwmSignal))
        self.speedProperty.value = targetSpeed

    def getCurrentSpeed(self):
        return self.convertToSpeed(self.currentPwmSignal)

    def getCurentPwmValue(self):
        return self.currentPwmSignal

    def isTargetDirection(self):
        return self.targetDirection


    def setTargetDirection(self, targetDirection: bool):
        self.targetDirection = targetDirection
        self.targetPwmSignal = self.convertToPwmSignal(self.targetDirection, self.targetSpeed)
        #self.getLogger().info("new target pwm: %d" % self.targetPwmSignal)
        self.directionProperty.value = "true" if targetDirection else "false"

    def isCurrentDirection(self):
        return self.isDirectionForward(self.currentPwmSignal)

    def isFlowDirectionIn(self):
        return not self.isCurrentDirection()

    def convertToSpeed(self, pwmSignal: int):
        return abs(pwmSignal - 125) / self.PWM_RANGE * 100


    def setCurrentPwmSignal(self, currentPwmSignal: int):
        self.currentPwmSignal = currentPwmSignal
        #print("%s new current pwm: %d" % (self.id, self.currentPwmSignal * 4))
        self.pwm.duty(int(self.currentPwmSignal * 4))


    def isDirectionForward(self, pwmSignal: int):
        directionForward = pwmSignal < 128
        return directionForward





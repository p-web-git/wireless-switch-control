mqttWled = None


def sendOnCommand(lowBrightness=False):
    global mqttWled
    mqttWled.send(msg='ON')


def sendOffCommand():
    global mqttWled
    mqttWled.send(msg='OFF')


def sendApiCommand(cmd):
    global mqttWled
    mqttWled.send('api', cmd)


def sendIncrementCommand(value):
    sendApiCommand('A=~' + str(value))

import globalVars


def sendOnCommand(lowBrightness=False):
    globalVars.mqttWled.send(msg='ON')


def sendOffCommand():
    globalVars.mqttWled.send(msg='OFF')


def sendApiCommand(cmd):
    globalVars.mqttWled.send('api', cmd)


def sendIncrementCommand(value):
    sendApiCommand('A=~' + str(value))

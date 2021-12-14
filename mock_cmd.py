def sendIncrementCommand(value):
	print(value, flush=True)

def sendOnCommand(lowBrightness=False):
	print("ON", flush=True)

def sendOffCommand():
	print("OFF", flush=True)

def sendApiCommand(cmd):
	print("API " + cmd, flush=True)


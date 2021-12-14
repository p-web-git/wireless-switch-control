from switch_states import SwithStateMachine
import switch_states

import logging
import time
import mqttClient
import json
import signal
import sys

def processNewEventOnSM(client, userdata, msg):
	global device
	payload = msg.payload.decode()
	ev = json.loads(payload).get('action')
	device.on_event(ev)

def sendApiCommand(cmd):
	global mqttWled
	mqttWled.send('api', cmd)

def sendIncrementCommand(value):
	sendApiCommand('A=~'+str(value))

def sendOnCommand(lowBrightness=False):
	global mqttWled
	mqttWled.send(msg='ON')

def sendOffCommand():
	global mqttWled
	mqttWled.send(msg='OFF')


logging.basicConfig(level=logging.DEBUG)
logging.info('Start')

termninateFlag = False

device = SwithStateMachine()

mqttWled = mqttClient.mqttClient(topic='wled/room', send_status = False)
switch_states.sendIncrementCommand = sendIncrementCommand
switch_states.sendOnCommand = sendOnCommand
switch_states.sendOffCommand = sendOffCommand
switch_states.sendApiCommand = sendApiCommand


mqttSwitch =  mqttClient.mqttClient(send_status = False)
mqttSwitch.subscribe('zigbee/wireless_switch/#')
mqttSwitch.recvHandler(processNewEventOnSM)

mqttWled.client.loop_start()
mqttSwitch.client.loop_forever()

mqttSwitch.close()
mqttWled.close()

logging.info('Exit')

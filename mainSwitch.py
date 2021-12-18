from switch_states import SwithStateMachine
from mqttClient import mqttClient
from dotenv import find_dotenv, load_dotenv
import os
import switch_states
import logging
import time
import json
import signal
import sys
import sentry_sdk

load_dotenv(find_dotenv())

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

sentry_sdk.init(
    os.getenv('SENTRY_SWITCH'),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

logging.basicConfig(format='%(levelname)-8s %(message)s', level=logging.DEBUG)
logging.info('Start')

termninateFlag = False

device = SwithStateMachine()

mqttWled = mqttClient(topic='wled/room', send_status = False)
switch_states.sendIncrementCommand = sendIncrementCommand
switch_states.sendOnCommand = sendOnCommand
switch_states.sendOffCommand = sendOffCommand
switch_states.sendApiCommand = sendApiCommand


mqttSwitch =  mqttClient(send_status = False)
mqttSwitch.subscribe('zigbee/wireless_switch/#')
mqttSwitch.recvHandler(processNewEventOnSM)

mqttWled.client.loop_start()
mqttSwitch.client.loop_forever()

mqttSwitch.close()
mqttWled.close()

logging.info('Exit')

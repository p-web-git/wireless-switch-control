from switchStateMachine import SwitchStateMachine
from mqttClient import mqttClient
from dotenv import find_dotenv, load_dotenv
import switchStateMachine
from wledCmd import *
import globalVars
import os
import logging
import json
import sentry_sdk


# Receive handlers to be called from the inside of mqtt, and send events to SM

def processNewEventOnSM(client, userdata, msg):
     if msg.topic == 'zigbee/bridge/state':
        payload = msg.payload.decode()
        state = json.loads(payload).get('state')
        if state == 'offline':
            logging.warning('Zigbee bridge is offline! isnt possible to receive command from the switch')
        elif state == 'online':
            logging.warning('Zigbee bridge is online')
     elif msg.topic == 'zigbee/switch/ikea':
        payload = msg.payload.decode()
        ev = json.loads(payload).get('action')
        globalVars.SSM.on_event(ev)
     else:
        logging.error('Zigbee: Unknown message')


def processFeedbackOnSM(client, userdata, msg):
    if msg.payload.decode() == '0':
        logging.debug('Detected Wled switch off')
        globalVars.SSM.on_event('off')
    else:
        logging.debug('Detected Wled switch on')
        globalVars.SSM.on_event('on')

sentry_sdk.init(
    os.getenv('SENTRY_SWITCH'),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


def _main():
    logging.basicConfig(format='%(levelname)-8s %(message)s', level=logging.INFO)
    logging.info('Start')

    load_dotenv(find_dotenv())

    global SSM

    mqttWled = mqttClient(topic='wled/room', send_status=False)
    globalVars.mqttWled = mqttWled
    mqttWled.subscribe('wled/room/g')

    SSM = SwitchStateMachine()
    globalVars.SSM = SSM
    switchStateMachine.sendOnCommand = sendOnCommand
    switchStateMachine.sendOffCommand = sendOffCommand
    switchStateMachine.sendIncrementCommand = sendIncrementCommand
    switchStateMachine.sendApiCommand = sendApiCommand

    mqttWled.recvHandler(processFeedbackOnSM)

    mqttSwitch = mqttClient(send_status=False)
    # mqttSwitch.subscribe('zigbee/wireless_switch/#')
    mqttSwitch.subscribe([('zigbee/switch/ikea', 0), ('zigbee/bridge/state', 0)])
    mqttSwitch.recvHandler(processNewEventOnSM)

    mqttWled.client.loop_start()
    mqttSwitch.client.loop_forever()

    mqttSwitch.close()
    mqttWled.close()

    logging.info('Exit')


if __name__ == '__main__':
    _main()

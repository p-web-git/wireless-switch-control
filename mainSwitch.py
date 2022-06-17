from switchStateMachine import SwitchStateMachine
from mqttClient import mqttClient
from wledCmd import *
from dotenv import find_dotenv, load_dotenv
import switchStateMachine
import os
import logging
import json
import sentry_sdk


# Global variables
SSM = None


# Receive handlers to be called from the inside of mqtt, and send events to SM

def processNewEventOnSM(client, userdata, msg):
    global SSM
    payload = msg.payload.decode()
    ev = json.loads(payload).get('action')
    SSM.on_event(ev)


def processFeedbackOnSM(client, userdata, msg):
    global SSM
    if msg.payload.decode() == '0':
        print('manually off')
        SSM.on_event('off')
    else:
        print('manually on')
        SSM.on_event('on')


sentry_sdk.init(
    os.getenv('SENTRY_SWITCH'),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


def _main():
    logging.basicConfig(format='%(levelname)-8s %(message)s', level=logging.DEBUG)
    logging.info('Start')

    load_dotenv(find_dotenv())

    global SSM, mqttWled
    SSM = SwitchStateMachine()

    mqttWled = mqttClient(topic='wled/room', send_status=False)
    mqttWled.subscribe('wled/room/g')
    mqttWled.recvHandler(processFeedbackOnSM)

    switchStateMachine.sendOnCommand = sendOnCommand
    switchStateMachine.sendOffCommand = sendOffCommand
    switchStateMachine.sendIncrementCommand = sendIncrementCommand
    switchStateMachine.sendApiCommand = sendApiCommand

    mqttSwitch = mqttClient(send_status=False)
    # mqttSwitch.subscribe('zigbee/wireless_switch/#')
    mqttSwitch.subscribe('zigbee/switch/ikea')
    mqttSwitch.recvHandler(processNewEventOnSM)

    mqttWled.client.loop_start()
    mqttSwitch.client.loop_forever()

    mqttSwitch.close()
    mqttWled.close()

    logging.info('Exit')


if __name__ == '__main__':
    _main()

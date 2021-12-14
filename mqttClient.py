import os
from dotenv import find_dotenv, load_dotenv
import logging

import paho.mqtt.client as mqtt

# find the dotenv file if it lives beside this script
load_dotenv(find_dotenv())

BROKER = '127.0.0.1'
PORT = 1883
USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')

def weakMessageHandler(client, userdata, msg):
	print(msg.topic, msg.payload.decode())

class mqttClient:
	def __init__(self, topic=None, send_status=True):
		self.topic = topic
		self.send_status = send_status
		self.first_send = True
		self.client = mqtt.Client()
		if self.send_status:
			self.client.will_set(self.topic + '/status', 'offline', qos=0, retain=True)
		self.client.username_pw_set(USERNAME, PASSWORD)
		self.client.connect(BROKER, PORT)
		self.client.on_message = weakMessageHandler

	def send(self, topic=None, msg=None):
		if self.send_status and self.first_send:
			self.client.publish(self.topic + '/status', 'online', retain=True)
		self.first_send = False
		if topic is not None:
			ret = self.client.publish(self.topic + '/' + topic, msg, retain=False)
			logging.debug(str('Publish: ' + self.topic + '/' + topic + ' - ' +  msg + '\tOutput: ' + str(ret.rc)))
		else:
			ret = self.client.publish(self.topic, msg, retain=False)
			logging.debug(str('Publish: ' + self.topic + ' - ' +  msg + '\tOutput: ' + str(ret.rc)))

	def sendObj(self, topic=None, obj=None):
		if type(obj) is dict:
			for k in list(obj.keys()):
				if topic:
					self.sendObj(str(topic + '/' + k), obj[k])
				else:
					self.sendObj(str(k), obj[k])
		else:
			self.send(topic, str(obj))

	def subscribe(self, topic):
		self.client.subscribe(topic)
		logging.debug(str('Subscribe: ' + topic))


	def recvHandler(self, fn):
		self.client.on_message = fn

	def close(self):
		logging.debug('Closing client')
		if self.send_status:
			self.client.publish(self.topic + '/status', 'offline', retain=True)
		self.client.loop_stop()
		self.client.disconnect()


def _main():
	import time

	logging.basicConfig(level=logging.DEBUG)

	client = mqttClient('test')
	client.send('abc', 10)


	log = {'fields': {'temperature': 18.27, 'humidity': 48.363, 'pressure': 1025.4}}
	client.sendObj("", log['fields'])

	client.send('mydevice', str(log['fields']))

	#client.subscribe('wled/#')
	client.subscribe('zigbee/wireless_switch/#')
	client.recvHandler(weakMessageHandler)

	client.client.loop_start()
	time.sleep(10)

	client.close()
	logging.info('Exit')

if __name__ == '__main__':
	_main()

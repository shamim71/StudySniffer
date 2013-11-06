#!/usr/bin/env python
from __future__ import print_function, division
from scapy.all import *
import time
import json
import hashlib

class StudySniffer():

	def __init__(self):
		self.clients = []
		self.clientTypes = (0, 2, 4)
		self.initTime = time.time()

		self.COUNT_INTERVAL = 10
		self.DISCO_INTERVAL = 30
		self.INTERFACE = "mon0"
		self.SERVER = "192.168.1.1"
		self.LOCATION = "The Moon"
		self.REMOTE_URL = "http://change.this.please.com/packets"

		self.loadConfig()

	def loadConfig(self):
		config = open("sniffer.conf", "r")
		for line in config:
			if (not "#" in line and ":" in line):
				option = line.split(":")[0].strip().lower()
				setting = line.split(":")[1].strip().lower()

				if option == "interface":
					self.INTERFACE = setting
				if option == "server":
					self.SERVER = setting
				if option == "location":
					self.LOCATION = setting
				if option == "disco_interval":
					self.DISCO_INTERVAL = setting
				if option == "count_interval":
					self.COUNT_INTERVAL = setting
				if option == "remote_url":
					self.REMOTE_URL = setting

	def getInterface(self):
		return self.INTERFACE

	def isTimeForDissociate(self):
		return time.time()-clientTime > self.DISCO_INTERVAL

	def noClientsInArray(self):
		return len(self.clients) == 0

	def isTimeToPrintStatistics(self):
		return time.time()-self.initTime > self.COUNT_INTERVAL

	def sniffWifi(self, packet):
		isUnique = True
		index = 0
		if (isTimeToPrintStatistics()):
			self.initTime = time.time()
			print("Client count: " + str(len(self.clients)))
			print("Study Spot Score (tm): " + str(self.scoreClients()))
		if packet.haslayer(Dot11):
			if packet.type == 0 and packet.subtype in self.clientTypes:
				if (noClientsInArray()):
					self.addClient(packet)
				for clientMac, clientSignal, clientTime  in self.clients:

					if (isTimeForDissociate()):
						print("Disassociate: " + clientMac)
						self.clients.pop(index)
					if packet.addr2 == clientMac:
						isUnique = False
						self.clients[index][1]=clientSignal
						self.clients[index][2]=time.time()

					index = index + 1

				if (isUnique):
					self.addClient(packet)

	def addClient(self, packet):
		mac = packet.addr2
		signal = -(256 - ord(packet.notdecoded[14]))
		originTime = time.time()
		self.clients.append([mac, signal, originTime])

		jsonResults = self.jsonEncapsulate(mac, signal, originTime)

		# Writing out to log. TODO: format should be changed to be more log friendly. 
		jsonOut = open("json-output.txt", "a")
		jsonOut.write(jsonResults)
		jsonOut.write("\n")
		jsonOut.close()

		urllib2..urlopen(REMOTE_URL,  urllib.urlencode(jsonResults))

		print(mac + "\t" + str(signal) + "dB" + "\t" + str(originTime))

	def scoreClients(self):
		score = 0.0
		for mac, signal, time in self.clients:
			score += (1 + abs(signal)/100)

		return score

	def jsonEncapsulate(self, mac, signal, time):
		oui = mac[0:8]
		hashMac = hashlib.sha512(mac).hexdigest()
		return json.JSONEncoder().encode({"id":hashMac, "oui":oui, "signal":signal, "time":time, "location":self.LOCATION})

if __name__ == "__main__":
	sniffer = StudySniffer()
	sniff(iface=sniffer.getInterface(), prn=sniffer.sniffWifi)	
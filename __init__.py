# Copyright (c) 2010-2017 by the respective copyright holders.

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from fuzzywuzzy import fuzz

import requests
import json

# v 0.1 - just switch on and switch off a fix light
# v 0.2 - code review
# v 0.3 - first working version on fixed light item
# v 0.4 - getTaggedItems method in order to get all the tagged items from OH
# v 0.5 - refresh tagged item intent
# v 0.6 - add findItemName method and import fuzzywuzzy
# v 0.7 - add intent for switchable items
# v 0.8 - merged lighting and switchable intent in onoff intent
# v 0.9 - added support to dimmable items

__author__ = 'mortommy'

LOGGER = getLogger(__name__)

class OpenHabSkill(MycroftSkill):
	
	def __init__(self):
		super(OpenHabSkill, self).__init__(name="OpenHabSkill")
				
		self.url = "http://%s:%s/rest" % (self.config.get('host'), self.config.get('port'))
				
		self.command_headers = {"Content-type": "text/plain"}
		
		self.polling_headers = {"Accept": "application/json"}
		
		self.lightingItemsDic = dict()
		self.switchableItemsDic = dict()
		self.getTaggedItems()		
			
	def initialize(self):
		self.load_data_files(dirname(__file__))
		
		refresh_labeled_items_intent = IntentBuilder("RefreshLabeledItemsIntent").require("RefreshLabeledItemsKeyword").build()
		self.register_intent(refresh_labeled_items_intent, self.handle_refresh_labeled_items_intent)
		
		onoff_status_intent = IntentBuilder("OnOff_StatusIntent").require("OnOffStatusKeyword").require("Command").require("Item").build()
		self.register_intent(onoff_status_intent, self.handle_onoff_status_intent)
		
		dimmer_status_intent = IntentBuilder("Dimmer_StatusIntent").require("DimmerStatusKeyword").require("Item").optionally("BrigthPercentage").build()
		self.register_intent(dimmer_status_intent, self.handle_dimmer_status_intent)
			
	def getTaggedItems(self):
		#find all the items tagged Lighting and Switchable from OH
		#the labeled items are stored in dictionaries
		
		self.lightingItemsDic = {}
		self.switchableItemsDic = {}
		requestUrl = self.url+"/items?recursive=false"
				
		try:
			req = requests.get(requestUrl, headers=self.polling_headers)
			if req.status_code == 200:
				json_response = req.json()
				for x in range(0,len(json_response)):
					if ("Lighting" in json_response[x]['tags']):
						self.lightingItemsDic.update({json_response[x]['name']: json_response[x]['label']})
					elif ("Switchable" in json_response[x]['tags']):
						self.switchableItemsDic.update({json_response[x]['name']: json_response[x]['label']})
					else:
						pass
			else:
				LOGGER.error("Some issues with the command execution!")
				self.speak_dialog('GetItemsListError')
				
		except KeyError:
					pass
	
	def findItemName(self, itemDictionary, messageItem):
		
		bestScore = 0
		score = 0
		bestItem = None		
		
		try:
			for itemName, itemLabel in itemDictionary.items():
				score = fuzz.ratio(messageItem, itemLabel)
				if score > bestScore:
					bestScore = score
					bestItem = itemName
		except KeyError:
                    pass
					
		return bestItem
	
	def handle_refresh_labeled_items_intent(self, message):
		#to refresh the oh items labeled list we use an intent, we can ask Mycroft to make the refresh
		
		self.getTaggedItems()
		dictLenght = str(len(self.lightingItemsDic) + len(self.switchableItemsDic))
		self.speak_dialog('RefreshLabeledItems', {'number_item': dictLenght})
	
	def handle_onoff_status_intent(self, message):
		
		command = message.data["Command"]
        messageItem = message.data["Item"]
				
		#We have to find the item to update from our dictionaries
		self.lightingSwitchableItemsDic = dict()
		self.lightingSwitchableItemsDic.update(self.lightingItemsDic)
		self.lightingSwitchableItemsDic.update(self.switchableItemsDic)
		
		ohItem = self.findItemName(self.lightingSwitchableItemsDic, messageItem)
		
		if ohItem != None:
			if (command != "on") and (command != "off"):
				self.speak_dialog('ErrorDialog')
			else:
				statusCode = self.sendCommandToItem(ohItem, command.upper())
				if statusCode == 200:
					self.speak_dialog('StatusOnOff', {'command': command, 'item': messageItem})
				elif statusCode == 404:
					LOGGER.error("Some issues with the command execution!. Item not found")
					self.speak_dialog('ItemNotFoundError')
				else:
					LOGGER.error("Some issues with the command execution!")
					self.speak_dialog('CommunicationError')
		else:
			LOGGER.error("Item not found!")
			self.speak_dialog('ItemNotFoundError')
	
	def handle_dimmer_status_intent(self, message):
		command = message.data.get('DimmerStatusKeyword')
		messageItem = message.data["DimmerItem"]
				
		statusCode = 0
		
		ohItem = self.findItemName(self.lightingItemsDic, messageItem)
		
		if ohItem != None:
			if (command == "set"):
				brightValue = message.data["BrigthPercentage"]
				if ((int(brightValue) < 0) or (int(brightValue) > 100)):
					self.speak_dialog('ErrorDialog')
				else:
					statusCode = self.sendCommandToItem(ohItem, brightValue)
			else:
				#find current item statusCode
				state = self.getCurrentItemStatus(ohItem)
				
				if (state != None):
					#dim or brighten the value by 10
					curBrightList = state.split(',')
					curBright = int(curBrightList[len(curBrightList)-1])
					
					if (command == "dim"):
						newBrightValue = curBright-10
					else:
						newBrightValue = curBright+10
				
					if (newBrightValue < 0):
						newBrightValue = 0
					elif (newBrightValue > 100):
						newBrightValue = 100
					else:
						pass
				
					#send command to item
					statusCode = self.sendCommandToItem(ohItem, str(newBrightValue))
			
			if statusCode == 200:
					self.speak_dialog('StatusDimmer', {'item': messageItem})
			elif statusCode == 404:
					LOGGER.error("Some issues with the command execution!. Item not found")
					self.speak_dialog('ItemNotFoundError')
			else:
					LOGGER.error("Some issues with the command execution!")
					self.speak_dialog('CommunicationError')
						
		else:
			LOGGER.error("Item not found!")
			self.speak_dialog('ItemNotFoundError')
	
	def sendStatusToItem(self, ohItem, command):
		requestUrl = self.url+"/items/%s/state" % (ohItem)
		req = requests.put(requestUrl, data=command, headers=self.command_headers)
		
		return req.status_code
			
	def sendCommandToItem(self, ohItem, command):
		requestUrl = self.url+"/items/%s" % (ohItem)
		req = requests.post(requestUrl, data=command, headers=self.command_headers)
		
		return req.status_code
		
	def getCurrentItemStatus(self, ohItem):
		requestUrl = self.url+"/items/%s/state" % (ohItem)
		state = None
				
		try:
			req = requests.get(requestUrl, headers=self.command_headers)
			
			if req.status_code == 200:
				state = req.text
			else:
				LOGGER.error("Some issues with the command execution!")
				self.speak_dialog('CommunicationError')
				
		except KeyError:
			pass
		
		return state
		
	def stop(self):
		pass
	 
def create_skill():
    return OpenHabSkill()
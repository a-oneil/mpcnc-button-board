#!/usr/bin/python3
from gpiozero import Button
from signal import pause
from octorest import OctoRest
from slack import WebClient
from dotenv import load_dotenv,dotenv_values
import requests,json,os

load_dotenv()
config=dotenv_values(os.getenv('ENVLOCATION'))

class HomeAssistant:
    HA_BASE_URL=config["HA_BASE_URL"]
    HA_KEY=config["HA_API_KEY"]
    headers = {'Authorization': f'Bearer {HA_KEY}','Content-Type': 'application/json'}
    
    def __init__(self):
        pass

    def post(self, payload, url):
        response = requests.request("POST", url, headers=self.headers, data=payload)

    def turnon_light(self, light, percentage):
        try:
			url = f"{self.HA_BASE_URL}/services/light/turn_on"
			self.payload = json.dumps({"entity_id": f"light.{light}","brightness_pct": f"{percentage}"})
			self.post(self.payload, url)
		except:
			print("turnon_light action failed")
	
    def turnoff_light(self, light):
        try:
			url = f"{self.HA_BASE_URL}/services/light/turn_off"
        	self.payload = json.dumps({"entity_id": f"light.{light}"})
        	self.post(self.payload, url)
		except:
			print("turnoff_light action failed")
	
    def toggle_light(self, light):
		try:
			url = f"{self.HA_BASE_URL}/services/light/toggle"
			self.payload = json.dumps({
			"entity_id": f"light.{light}",
			})
			self.post(self.payload, url)
		except:
			print("toggle_light action failed")

    def toggle_switch(self, switch):
		try:
			url = f"{self.HA_BASE_URL}/services/switch/toggle"
			self.payload = json.dumps({"entity_id": f"switch.{switch}"})
			self.post(self.payload, url)
		except:
			print("toggle_switch action failed")

    def turn_off_switch(self, switch):
		try:
			url = f"{self.HA_BASE_URL}/services/switch/turn_off"
			self.payload = json.dumps({"entity_id": f"switch.{switch}"})
			self.post(self.payload, url)
		except:
			print("turn_off_switch action failed")

    def turn_on_switch(self, switch):
		try:
			url = f"{self.HA_BASE_URL}/services/switch/turn_on"
			self.payload = json.dumps({"entity_id": f"switch.{switch}"})
			self.post(self.payload, url)
		except:
			print("turn_on_switch action failed")

    def run_automation(self, automation):
		try:
			url = f"{self.HA_BASE_URL}/services/automation/trigger"
			self.payload = json.dumps({"entity_id": f"automation.{automation}"})
			self.post(self.payload, url)
		except:
			print("run_automation action failed")

    def run_script(self, script):
		try:
			url = f"{self.HA_BASE_URL}/services/script/turn_on"
			self.payload = json.dumps({"entity_id": f"script.{script}"})
			self.post(self.payload, url)
		except:
			print("run_script action failed")

# Setup classes
ha = HomeAssistant()
octoapi = OctoRest(url=config["OCTOPRINT_URL"], apikey=config["OCTOPRINT_API"])
slackapi = WebClient(config["SLACK_BOT_TOKEN"])

# Setup Counters
held_for = 0.0
trigger1time = 0.1
trigger2time = 1.0
trigger3time = 2.0

# Octoprint Gcode Command List
HOME_XY = ["G28 X Y"]
XYZ_GT_WPH = ["G0 Z40.0000 F800", "G0 X0.0000 Y0.0000 F2100", "G0 Z0.0000 F800"]
DISABLE_Z = ["M18 Z"]
ZERO_XYZ_PROBE = ["G90","G92 X0 Y0 Z0","G00 Z5.0000 F500","G28 Z","G92 Z0.5","G00 Z15 F500","G4 P15000","G00 Z0.0000 F500"]
ZERO_XYZ_NO_PROBE = ["G92 X0 Y0 Z0"]

# Function to post a message to slack, configured by SLACK_DEFAULT_CHANNEL in env 
def post_message(message=None, channel=config["SLACK_DEFAULT_CHANNEL"], blocks=None, files=None):
	try:
		message = "MPCNC: " + message
		slackapi.chat_postMessage(channel=channel, text=message, blocks=blocks, file=files)
	except:
		print("Failed to post message to slack")

# Setup button release & noise Message
def release(held_for,button):
	print(f"{button} held for {held_for} seconds.")  

def noise_message(button):
	print(f"{button} Held for under {trigger1time} seconds, probably noise...")

## Button Hold Function - Holdtime Counter ##
def cncbutton_hld():
	global held_for
	held_for = max(held_for, cncbutton.held_time + cncbutton.hold_time)
	release(held_for,"CNC Button")

def vacuumbutton_hld():
	global held_for
	held_for = max(held_for, vacuumbutton.held_time + vacuumbutton.hold_time)
	release(held_for,"Vacuum Button")

def lightbutton_hld():
	global held_for
	held_for = max(held_for, lightbutton.held_time + lightbutton.hold_time)
	release(held_for,"Lights Button")

def multibutton_hld():
	global held_for
	held_for = max(held_for, multibutton.held_time + multibutton.hold_time)
	release(held_for,"Multi Button")

## Button Release Functions - Execute commands ##

# Trigger 1 - Toggle CNC
# Trigger 2 - Home XY
def cncbutton_rls():
	try:
		global held_for
		release(held_for,"CNC Button")
		if (held_for >= trigger1time) and (held_for < trigger2time):
			print('Toggling CNC E-STOP')
			ha.toggle_switch("cnc_estop")
		elif (held_for >= trigger2time):
			print("Home XY")
			octoapi.gcode(HOME_XY)
			post_message("Home XY initated")
		elif (held_for < trigger1time):
			noise_message("CNC Button")
		held_for = 0.0
	except:
		print("CNC button action failed!")

# Trigger 1 - Toggle Vacuum
# Trigger 2 - XYZ GT WPH
# Trigger 3 - Disable Z
def vacuumbutton_rls():
	try:
		global held_for
		release(held_for,"Vacuum Button")
		if (held_for >= trigger1time) and (held_for < trigger2time):
			print('Toggling Vacuum')
			ha.toggle_switch("garage_vacuum")
		elif (held_for > trigger2time) and (held_for < trigger3time):
			print("XYZ_GT_WPH")
			post_message("XYZ go to WPH initated")
			octoapi.gcode(XYZ_GT_WPH)
		elif (held_for >= trigger3time):
			print("DISABLE_Z")
			octoapi.gcode(DISABLE_Z)
			post_message("Z Axis Disabled")
		else:
			noise_message("Vacuum Button")
		held_for = 0.0
	except:
		print("Vacuum button action failed!")

# Trigger 1 - Toggle CNC Lights
# Trigger 2 - Zero XYZ w/ Probe		
def lightbutton_rls():
	try:
		global held_for
		release(held_for,"Lights Button")
		if (held_for >= trigger1time) and (held_for < trigger2time):
			print('Toggling Lights')
			ha.toggle_switch("cnc_lights")
		elif (held_for >= trigger2time):
			print("ZERO_XYZ_PROBE")
			octoapi.gcode(ZERO_XYZ_PROBE)
			post_message("Zero XYZ With Probe initated")
		elif (held_for < trigger1time):
			noise_message("Lights Button")
		held_for = 0.0
	except:
		print("Light button action failed!")

# Trigger 1 - Toggle Garage Fan
# Trigger 2 - Zero XYZ w/o Probe     
def multibutton_rls():
	try:
		global held_for
		release(held_for,"Multi Button")
		if (held_for >= trigger1time) and (held_for < trigger2time):
			print('Toggling Fan')
			ha.toggle_switch("garage_fan")
		elif (held_for >= trigger2time):
			print("ZERO_XYZ_NO_PROBE")
			octoapi.gcode(ZERO_XYZ_NO_PROBE)
			post_message("Zero XYZ With No Probe initated")
		elif (held_for < trigger1time):
			noise_message("Mutli Button")
		held_for = 0.0
	except:
		print("Multi button action failed!")

cncbutton=Button(21, hold_time=trigger1time, hold_repeat=True, pull_up = False)
vacuumbutton=Button(20, hold_time=trigger1time, hold_repeat=True, pull_up = False)
lightbutton=Button(19, hold_time=trigger1time, hold_repeat=True, pull_up = False)
multibutton=Button(16, hold_time=trigger1time, hold_repeat=True, pull_up = False)

if __name__ == "__main__":
	try:
		cncbutton.when_held = cncbutton_hld
		cncbutton.when_released = cncbutton_rls
		vacuumbutton.when_held = vacuumbutton_hld
		vacuumbutton.when_released = vacuumbutton_rls
		lightbutton.when_held = lightbutton_hld
		lightbutton.when_released = lightbutton_rls
		multibutton.when_held = multibutton_hld
		multibutton.when_released = multibutton_rls
		pause()
	except Exception as e:
		post_message(e)

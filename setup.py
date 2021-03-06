import subprocess
from subprocess import call
from subprocess import Popen
from subprocess import check_output
from subprocess import check_call
from subprocess import PIPE
from subprocess import CalledProcessError
import sys

# VARIABLES
SNIFFER_LOCATION    = "/root/git/StudySniffer/StudySniffer.py"
INTERFACE           = ""
NETCTL_PROFILE_NAME = ""			
NETCTL_SETTINGS     = ""

# STRINGS
FAIL                 = "[FAIL]"
SUCC                 = "[GOOD]"
INIT                 = "[INIT]"
DEF                  = "[ -- ]"
INTERFACE_COUNT_FAIL = FAIL + "Not enough wireless adapters detected. Exiting...\n"
BANNER               = "\n"
BANNER               += "***************************** \n"
BANNER               += "*  Study Spot Sniffer v0.0  * \n"
BANNER               += "***************************** \n"

# FUNCTIONS
def loadConfig():
	settingsFlag	= False
	netctlFlag		= False
	global NETCTL_SETTINGS
	global NETCTL_PROFILE_NAME
	global INTERFACE

	config = open("sniffer.conf", "r")
	for line in config:
		if ( line.strip() != "" ):
			if ( line.strip()[0] != "#" ):
				if ( "!" in line ):
					settingsFlag = False
					netctlFlag   = False
					if ( "settings" in line ):
						settingsFlag = True
					if ( "netctl" in line ):
						netctlFlag = True
					continue

				if ( netctlFlag ):
					option = line.split("=")[0].strip()
					setting = line.split("=")[1].strip()

					NETCTL_SETTINGS += ( option + "=" + setting + "\n" )

				if ( settingsFlag ):
					option = line.split("=")[0].strip().lower()
					setting = line.split("=")[1].strip().lower()

					if option == "interface":
						INTERFACE = setting
					if option == "netctl_profile_name":
						NETCTL_PROFILE_NAME = setting


def generateNetctlProfile( interface ):
	filePath = "/etc/netctl/" + NETCTL_PROFILE_NAME

	TEMP_NETCTL_SETTINGS = NETCTL_SETTINGS + ("Interface=" + interface)

	file = open(filePath, "w")
	file.write(TEMP_NETCTL_SETTINGS)
	file.close()

def countInterfaces():
	count = 0

	result = check_output(["iwconfig"], universal_newlines=True, stderr=subprocess.STDOUT )

	for line in result.split("\n"):
		if "wlan" in line:
			count += 1
	if (count < 2):
		sys.exit( INTERFACE_COUNT_FAIL )

	return count

# MAIN
def start():
	print ( BANNER )

	loadConfig()

	interface_count    = countInterfaces()
	monitorInitialized = False
	networkConnected   = False

	for i in range( 0, interface_count ):

		WLAN 		= "wlan" + str(i)

		# POPEN COMMANDS
		monitor_setup  = ["iw", "dev", WLAN, "interface", "add", INTERFACE, "type", "monitor"]
		monitor_enable = ["ip", "link", "set", INTERFACE, "up"]
		disconnect_all = ["netctl", "stop-all"]
		connect        = ["netctl", "start", NETCTL_PROFILE_NAME ]

		if ( not monitorInitialized ):
			try:
				check_output( monitor_setup, stderr=subprocess.STDOUT )
				check_output( monitor_enable, stderr=subprocess.STDOUT )
				monitorInitialized = True
				print ( SUCC, "Monitor mode enabled:", WLAN)
			except CalledProcessError as e:
				if ( e.returncode == 234 ):
					print ( FAIL, "Device doesn't support monitor mode:", WLAN )
				if ( e.returncode == 233 ):
					monitorInitialized = True
					print ( SUCC, "Device already in monitor mode:", WLAN )

		if ( not networkConnected ):
			try:
				generateNetctlProfile( WLAN )
				check_output( connect, stderr=subprocess.STDOUT )
				networkConnected = True
				print ( SUCC, "Network connection established:", WLAN)
			except CalledProcessError as e:
				if ( e.returncode == 1 ):
					print ( FAIL, "Unable to establish network connection:", WLAN )

		if ( monitorInitialized and networkConnected ):
			print ()
			print ( DEF, "All components initialized successfully." )
			break;

	if (monitorInitialized and networkConnected):
		print ( DEF, "Starting Study Sniffer...\n" )
		Popen( ["python2", SNIFFER_LOCATION], stderr=subprocess.STDOUT )

if __name__ == "__main__":
	start()

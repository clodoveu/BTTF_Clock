#
# BTTF Clock
#
# Global variable definitions
#
# CADJ 28/12/2018

#
# GLOBALS
#
import threading
from gpiozero import Button
from gpiozero import Buzzer

ClockMode = 1 # Current clock mode
DefaultClockMode = 1 # modifiable in the parameters file
paramFile = ".BTTF_Clock" # name of the parameters file
parameters = {} # dict of parameters
Deadline = "2019-12-31  23:59" # default deadline for the TimeToDeadline mode
FromDate = "1963-08-03 07:30"  # default starting date for the TimeSinceDate mode
MP3_Vol = 50  # MPC volume level
Brightness = 15 # Display brightness level
MP3_Source = "/home/pi/Music/"  # Directory for music files
RadioSource = "/home/pi/Radio/" # Directory for radio station lists
RadioList = "radioStations.txt"
RingtonesSource = '/home/pi/Ringtones/' # Directory for alarm ringtones
MP3_Filter = ''  # Filter for MP3 files to include in the playlist
AlarmTone = 0   # Default alarm sound: 0 = buzzer, 1 and above take the nth item in the Ringtones list
Locale = "pt-BR"

TimeZones = [] # list of time zones
timezonesFile = ".BTTF_timezones"

# Button objects from gpiozero
B = []
B.append(Button(12, hold_time = 0.2, hold_repeat = True)) # B[0]
B.append(Button(22)) # B[1]
B.append(Button(23)) # B[2]
B.append(Button(24)) # B[3]
B.append(Button(25)) # B[4]
B.append(Button(27)) # B[5]

BUZZ = Buzzer(13)
running = threading.Event()  # Event to catch the end of the program and finish threads and infinite loops
running.set()
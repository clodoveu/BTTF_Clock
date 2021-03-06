# BTTF_Clock
A Back to the Future clock, implemented in hardware and software using A Raspberry Pi Zero and Python code
The project is inspired by https://www.instructables.com/id/A-Back-to-the-Future-Clock/ but with significant hardware
and software differences.

Back to the Future clock
Documentation
CADJ - 2019-01-05

# 1. Hardware Modules

- Raspberry Pi Zero W
(https://www.amazon.com/gp/product/B0748MPQT4/ref=ppx_od_b_detailpages01?ie=UTF8&psc=1)
$26.99
  * includes a Raspberry Pi power source, 5V 2.5A, double pin header, heatsink
  * not used: case, micro USB OTG, mini HDMI to HDMI adapter

- 16 GB microSD card
about $7

- Adafruit I2S 3W Stereo Speaker Bonnet for Raspberry Pi
(https://www.amazon.com/gp/product/B01MXYBVKZ/ref=ppx_od_b_detailpages06?ie=UTF8&psc=1)
$13.89

- CQRobot Arduino Speaker 3 Watt 8 Ohms
(https://www.amazon.com/gp/product/B0738NLFTG/ref=oh_aui_detailpage_o00_s01?ie=UTF8&psc=1)
$7.87

- 4 x Quad alphanumeric display, red 0.54" digits, with I2C backpack
(https://www.amazon.com/gp/product/B00L2X4JEW/ref=ppx_od_b_detailpages01?ie=UTF8&psc=1)
$15.57 each

Additional hardware (total cost about $6):
- 7 push buttons
- single 20-pin header
- buzzer
- wiring
- a corner cut from a small prototype printed circuit board

A later addition: a DHT-22 temperature and humidity sensor

Case, which I designed and built using MDF and lucite.


# 2. Connections

Stereo speaker bonnet connects directly to the Pi zero's GPIO. I soldered a header to the bonnet's top
so that most GPIO pins remained accessible. I also soldered headers to the triple 3-pin power and ground connections
available in the top side of the bonnet. I then used female connectors to reach the display, buttons, and whatever else.

Display uses I2C, so the four modules were assembled in line. Their addresses were set to 0x70, 0x71, 0x72 and 0x73.

Wiring to the display used five strands of parallel wire for each, connecting everything to the printed circuit board,
in which I soldered five sets of five header pins, corresponding to V+ (power), V+ (logical level), Ground,
and SDA and SCL ports. One header was connected to each display, and the fifth to pins 1 (3.3V)
(twice, using the bonnet's header), 3, 5 and 6.

The stereo speaker bonnet uses GPIO pins 18, 19 and 21, so those are unavailable for other connections.

Buttons were then connected to the available GPIO pins: 12 (B0), 22 (B1), 23 (B2), 24 (B3), 25 (B4), 27 (B5). 
The other side of the buttons is connected to ground.

The DHT-22 sensor is connected to 3.3V, ground and GPIO pin 17. 

I also connected a buzzer to pin 13, and used pin 16 to connect a shutdown pushbutton (B6).


# 3. Software components

I installed Raspbian in the SD card, even though I would not use the GUI. 

After booting, user is pi and password is raspberry.

Run:

``` 
sudo raspi-config
```
And setup network options (hostname, WiFi), Localisation options (keyboard layout, time zone, locale), 
Advanced options (expand filesystem, memory split -- remove memory from the GPU, not needed), Interface options (enable
SSH and I2C)

Edit /etc/hosts and change the last line to reflect the hostname:

```
127.0.0.1 bttf_clock
```

Reboot and check if WiFi is working, then install utilities:

```
apt-get update
apt-get install vim
apt-get install git
```

From the basic installation, activate SSH and GPIO, and also maybe VNC.

All the software was written in Python 3.

### Python installation:

```
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus python-imaging git
```

### Adafruit display driver
See https://learn.adafruit.com/led-backpack-displays-on-raspberry-pi-and-beaglebone-black/overview 

```
git clone https://github.com/adafruit/Adafruit_Python_LED_Backpack.git
cd Adafruit_Python_LED_Backpack
sudo python3 setup.py install
```

### Stereo speaker bonnet
See https://learn.adafruit.com/adafruit-speaker-bonnet-for-raspberry-pi/raspberry-pi-usage

```
curl -sS
https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2samp.sh | bash
```

I took the additional step of activating the aplay script, but aplay caused all sorts of problems for me,
and I ended up removing it.

### MPD / MPC
The project uses MPD (Music Player Daemon) and MPC (Music Player Client), which run at the operating system level.
Controls are simple calls to MPC with the appropriate command-line attribute using the call function of the
processing Python module.

```
sudo apt-get install mpd mpc
```

MPC commands (see man page): https://www.mankier.com/1/mpc

MPD configuration: edit file /etc/mpd.conf
See https://linux.die.net/man/5/mpd.conf for details

In my setup, the relevant parts of the file are listed below. Notice that you need to create the .mpd folder and
define a Music folder.

```
music_directory	        "/home/pi/Music"
playlist_directory		"/home/pi/.mpd/playlists"
db_file			        "/home/pi/.mpd/mpd.db"
log_file			    "/home/pi/.mpd/mpd.log"
pid_file			    "/home/pi/.mpd/pid"
state_file			    "/home/pi/.mpd/state"
sticker_file            "/home/pi/.mpd/sticker.sql"
bind_to_address			"127.0.0.1"
log_level			    "default"
audio_output {
	type		    "alsa"
	name		    "My ALSA Device"
	device		    "hw:0,0"
	mixer_type      "software"
	mixer_control	"PCM"
}
connection_timeout	"2000000"
```

### Temperature and humidity sensor DHT-22
See https://tutorials-raspberrypi.com/raspberry-pi-measure-humidity-temperature-dht11-dht22/

Uses the Adafruit DHT library, installed as follows:

```
git clone https://github.com/adafruit/Adafruit_Python_DHT.git 
cd Adafruit_Python_DHT
sudo python setup.py install
```


### Python libraries and modules:

- Installed (with sudo pip3):
  - [gpiozero](https://gpiozero.readthedocs.io/en/stable/index.html#)
  - [unidecode](https://pypi.org/project/Unidecode/)
  - [xmltodict](https://pypi.org/project/xmltodict/)
  - [icu](https://pypi.org/project/PyICU/)

- Built-in:
  - urllib
  - threading
  - subprocess
  - signal
  - sys
  - csv
  - datetime
  - time
  - re

- Adafruit
  - Adafruit_DHT
  
# 4. Configuration

A configuration file (.BTTF_Clock) should be found in the application's folder.
First lines starting with # will be ignored. The first line of the file must be kept, as it is read using CSV.

```
parameter,value
# Comment
# Deadline format: yyyy-mm-dd hh:mm
Deadline,2019-01-01 00:00
# Days from date: yyyy-mm-dd hh:mm
FromDate,2018-01-01 00:00
# Default volume: 0 to 100 (MPC)
MP3_Vol,50
# Default Clock Mode
DefaultClockMode,1
# Default display brightness, 1 to 15
Brightness,0
# Filter for MP3 playlist creation
# MPC style: artist <keyword>  or title <keyword>
#     other types: album, genre, filename, any
# If empty, the entire Music folder will be used in the playlist
# Multiple clauses can be included, separated with |
# Examples:
#MP3_Filter,artist Queen
#MP3_Filter,artist "Bee Gees"
#MP3_Filter,title love
#MP3_Filter,genre classical
#MP3_Filter,artist "Bee Gees" | any Queen | artist Floyd | title Jagger
#MP3_Filter,any Raul
MP3_Filter,
# Source directory for music files. Recursive search. End with '/'
MP3_source,/home/pi/Music/
# Source directory for internet radio stations, file radioStations.txt
RadioSource,/home/pi/Radio/
# Source directory for ringtones (alarm sounds)
RingtonesSource,/home/pi/Ringtones/
# Filename for the list of radio stations
RadioList,radioStations.txt
# Default alarm tone, 0 = buzzer
AlarmTone,2
# Locale
Locale,pt_BR
# CityCode, according to CPTEC/INPE, BH = 222
CityCode,222
# AirportCode, according to CPTEC/INPE, BH = SBBH
AirportCode,SBBH
```

A list of valid time zones for the World Clock should be found in the application's folder.
First lines starting with # will be ignored.
The first attribute is the official time zone name, and shouldn't be changed. The second is the string that will
be displayed in the clock. The other attributes indicate whether the time zone is current (canonical),
an alias or deprecated, and the time differences to UTC in normal times and in daylight savings time

```
# Sample
America/Sao_Paulo;Brasilia;Canonical;-03:00;-02:00
America/Bahia;Bahia;Canonical;-03:00;-03:00
America/Cuiaba;Cuiaba;Canonical;-04:00;-03:00
America/Manaus;Manaus;Canonical;-04:00;-04:00
America/Rio_Branco;Acre;Canonical;-05:00;-05:00
America/New_York;New York;Canonical;-05:00;-04:00
America/Chicago;Chicago;Canonical;-06:00;-05:00
America/Denver;Denver;Canonical;-07:00;-06:00
...
```

# 5. Data directories

Three directories are expected: one for music (MP3), one for radio stations, and one for alarm ringtones (also MP3).

In the radio stations folder, a file called radioStations.txt is expected. It should contain URLs of radio streaming
services, one per line. After the comma, there is an optional description. Lines starting with # are ignored.

``` 
# Sample
http://sky1.torontocast.com:9085/stream, Radio BlueMoon Toronto
http://198.58.98.83:8258/stream, Classic Rock Florida HD
http://uk7.internet-radio.com:8226/stream, Box UK Radio danceradiouk
http://212.71.250.12:8040/stream, Merge 104.8 Oman
http://139.162.245.57:8256/stream, 80s Soundtracks Radio
http://uk6.internet-radio.com:8175/stream, SPARKS.FM UK RADIO
http://158.69.38.194:9098/stream, Cinemix
...
```

# 6. Weather information

I developed a module to get and print in the 16-digit alphanumeric display two types of weather information: current
weather and 4-day forecasts. Both are for Brazil and come from CPTEC/INPE, See http://servicos.cptec.inpe.br/XML/

The module also contains code for the temperature and humidity sensor, DHT-22.

# 7. Initialization at boot

A bash script is used in the home directory:

```
clock_init.sh  # remember to chmod to 755

cd ~/BTTF_Clock
python3 BTTF_Clock.py >> ./log.txt &
```

The script is then called up by /etc/rc.local:

```

(...)
/home/pi/clock_init.sh

exit 0

```


# 8. Operation

Modes       Player  Chrono  Clock   Chess
Button 1    Rew     Reset   --      Left player
Button 2    Vol-    --      Set-    Set-
Button 3    Play    Go      Go      Go
Button 4    Vol+    Stop    Set+    Set+
Button 5    Fwd     Cancel  Cancel  Right player

Button      1       2       3       4       5
Player      Rew     Vol-    Play    Vol+    Fwd
Clock       --      Set-    Go      Set+    Cancel
Chrono      Reset   --      Go      Stop    Cancel
Chess       LeftPl  Set-    Go      Set+    RightPl

Button 0    Mode change (short press)
            Back to default mode (long press)

Button 6    Brightness change (short press)
            Shutdown (long press), button 3 to confirm, button 5 to cancel
            
Button 2 + Button 4 in Mode 1 (BTTF clock): reload parameters file
Button 1 + Button 5 in Mode 1 (BTTF clock): terminate program, Button 3 to confirm 

# 9. Functions

1. Back to the Future Clock: a clock in the format [MMM dd YYYY hh.mm] as in the movie

2. Current weather: description from CPTEC/INPE of the current weather at the configured location

3. Weather 1- to 4-day forecast: from CPTEC/INPE, number of days is configurable

4. Time since date: time difference between now and a configured initial date

5. Time to deadline: time remaining until a given deadline

6. World clock: dates and times at several time zones, identified by representative cities, with indication of DST

7. MP3 player: plays MP3 files in th device's SD card

8. Internet radio: streams internet radio stations, choosing from a configurable list

9. Seconds clock: a clock in the format [DoW dd/MM hh.mm.ss]

10. Milliseconds clock: a clock in the format [dd/MM hh.mm.ss.mmm]

11. Milliseconds chronometer

12. Seconds chronometer

13. Year-long alarm: set an alarm for a month, day, hour and minute. Alarm tones are configurable, or use the buzzer

14. Timer: set hour, minute and second for a countdown

15. Chess clock: set countdown game times for whites and blacks, set board side, buzzer when the time runs out

16. IP address: show the device's IP address 



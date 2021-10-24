import RPi.GPIO as GPIO
import time
import os
import random
from os import listdir
from os.path import isfile, join
import subprocess
import alsaaudio
import vlc
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn



# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
vol = AnalogIn(mcp, MCP.P0) # Port 0 (P0) is volume
tuner = AnalogIn(mcp, MCP.P1) # Port 1 (P1) is the "tuner", 64-65000

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # The Shadow
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) # The Lone Ranger
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CHQR
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CFAC
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Music
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Stopall

# Setup some variables

state = "notplaying"
now_playing = ""
stream_type = ""

tunervalue = tuner.value
stations = {}
stations["cfac"] = "https://rogers-hls.leanstream.co/rogers/cal960.stream/playlist.m3u8"
stations["chqr"] = "https://live.leanstream.co/CHQRAM"

# Set up VLC

instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
player=instance.media_player_new()
#soundplayer=instance.media_player_new()

# Mixer for volume

m = alsaaudio.Mixer()

# routines and methods

def play(show):
    stop()
    print (show)
    episodedirectory = "/opt/radio/shows/" + show + "/"
    episodes =  [f for f in listdir(episodedirectory) if isfile(join(episodedirectory, f))]
    episode = episodedirectory + episodes[random.randrange(0,len(episodes))]
    
    media=instance.media_new(episode)
    player.set_media(media)
    player.play()

    state = "playing"
    now_playing = show
    stream_type = "radioshow"
    return (state,now_playing,stream_type)
    
def playradio(station):
    stop()
    media=instance.media_new(stations[station])
    player.set_media(media)
    player.play()

    state = "playing"
    now_playing = station
    stream_type = "radiostream"
    return (state,now_playing,stream_type)

def stop():
    if str(player.get_state()) == "State.Playing":
        player.stop()
    state = "notplaying"
    now_playing = ''

while True:

    the_shadow = GPIO.input(18)
    the_lone_ranger = GPIO.input(23)
    stopall = GPIO.input(24)
    chqr = GPIO.input(21)
    cfac = GPIO.input(27)
    music = GPIO.input(22)
    #motionsensor = GPIO.input(17)

    if the_shadow == False:
        (state,now_playing,stream_type) = play("theshadow")
        time.sleep(0.5)
    if the_lone_ranger == False:
        (state,now_playing,stream_type) = play("theloneranger")
        time.sleep(0.5)
    if chqr == False:
        (state,now_playing,stream_type) = playradio("chqr")
        time.sleep(0.5)
    if cfac == False:
        (state,now_playing,stream_type) = playradio("cfac")
        time.sleep(0.5)
    if music == False:
        (state,now_playing,stream_type) = play("music")
        time.sleep(0.5)

    if stopall == False:
        print(str(player.get_state()))
        stop()





    ## Set volume
    if vol.value >= 65000:
        volume = 100
    else:
        volume = float(vol.value) / 65000 * 100
    #print(int(volume))
    if state == "playing":
        tunervalue = tuner.value
    #print (tuner.value)
    #print(str(player.get_state()))
    #print(stream_type)
    if str(player.get_state()) == "State.Ended" and stream_type == "radioshow":
        play(now_playing)
    m.setvolume(int(volume))
    time.sleep(0.1)

import pyaudio
import math
import struct
import wave
import time
import os
import configparser
import json
import subprocess
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from picamera import PiCamera

import cv2
import numpy as np
from Adafruit_PCA9685 import PCA9685
import time
from getkey import getkey, keys

pwm = PCA9685(0x40)
pwm.set_pwm_freq(60)
y_value = 200
x_value = 300
pwm.set_pwm(0,0,x_value)
pwm.set_pwm(1,0,y_value)

# function to understand it telegram bot is running
def start(update, context):
    update.message.reply_text('Bot is active')

# Sending audio files via telegram bot
def send_audio(update):
    update.reply_audio(audio=open('records/0.wav','rb'))

def start_streaming(update,context):
	start_streamer()

def stop_streaming(update,context):
	stop_streamer()

def move_right(x_value,v):
    try:
        pos = int(v)
        if 20 <= pos <= 50:
            x_value -= pos
            x_value = max([min([x_value,600]),110])
        elif pos < 20:
            x_value -= 20
        elif pos > 50:
            x_value = pos
        return x_value
    except:
        return False

def move_left(x_value,v):
    try:
        pos = int(v)
        if 20 <= pos <= 50:
            x_value += pos
            x_value = max([min([x_value,600]),110])
        elif pos < 20:
            x_value += 20
        elif pos > 50:
            x_value = pos
        return x_value
    except:
        return False

def move_down(y_value,v):
    try:
        pos = int(v)
        if 5 <= pos <= 30:
            y_value += pos
            y_value = max([min([y_value,280]),120])
        elif pos < 5:
            y_value += 5
        elif pos > 30:
            y_value = pos
        return y_value
    except:
        return False

def move_up(y_value,v):
    try:
        pos = int(v)
        if 5 <= pos <= 30:
            y_value -= pos
            y_value = max([min([y_value,280]),120])
        elif pos < 5:
            y_value -= 5
        elif pos > 30:
            y_value = pos
        return y_value
    except:
        return False

# Moving servo via telegram bot
def move(update, context):
    message = update.message.text.split(' ')

    global x_value
    global y_value

    if len(message) < 3:
        update.message.reply_text('Write: \move left|right|up|down numeric_value')
    if message[1] == 'left':
        x_value = move_left(x_value,message[2])
        if not x_value:
            update.message.reply_text('Insert a valid number')
        else:
            horizontal_mvt(x_value)
    elif message[1] == 'right':
        x_value = move_right(x_value,message[2])
        if not x_value:
            update.message.reply_text('Insert a valid number')
        else:
            horizontal_mvt(x_value)
    elif message[1] == 'up':
        y_value = move_up(y_value,message[2])
        if not y_value:
            update.message.reply_text('Insert a valid number')
        else:
            vertical_mvt(y_value)
    elif message[1] == 'down':
        y_value = move_down(y_value,message[2])
        if not y_value:
            update.message.reply_text('Insert a valid number')
        else:
            vertical_mvt(y_value)
    else:
        update.message.reply_text('Write: \move horizontal|vertical numeric_value')
    print (x_value, y_value)

# move the servo left
def horizontal_mvt(pos):
	pwm.set_pwm(0, 0, pos)

# move the servo left
def vertical_mvt(pos):
	pwm.set_pwm(1, 0, pos)

# Sending picture files via telegram bot
def send_picture(update, context):
	dummy=True
	try:
        # check if the camera is busy streaming and kills the streamer
		stop_streamer()
		print('Found and destroyed streamer')
	except:
		dummy=False
	take_picture()
	update.message.reply_photo(photo=open('pictures/picture.jpg', 'rb'))
	if dummy:
        # if we were streaming, we restart the streamer
		print('Restarting streamer')
		start_streamer()

# finds the process id to kill
def pid_to_kill(process):
	l = process.split('        ')
	return(l[1][:4])

# stops the streamer
def stop_streamer():
	ps   = subprocess.Popen(['ps','-ef'],    shell=False, stdout=subprocess.PIPE)
	grep = subprocess.Popen(['grep', 'python'], shell=False, stdin=ps.stdout, stdout=subprocess.PIPE)
	grep_output,_ = grep.communicate()
	pid = pid_to_kill([s for s in grep_output.decode("utf-8").split('\n') if 'streamer.py' in s][0])
	subprocess.Popen(['kill','-9',pid],stdout=subprocess.PIPE)

# start streamer
def start_streamer():
	process = subprocess.Popen(['python3','streamer.py','&'], shell=False, stdout=subprocess.PIPE)

# takes picture with the camera
def take_picture():
	camera = PiCamera()
	camera.start_preview()
	camera.capture('pictures/picture.jpg')
	camera.stop_preview()
	camera.close()





## Experimental functions

## function to handle the /help command
#def help(update, context):
#    update.message.reply_text('help command received')

## function to handle errors occured in the dispatcher
#def error(update, context):
#    update.message.reply_text('an error occured')

## function to handle normal text
#def text(update, context):
#    text_received = update.message.text
#    update.message.send_text(f'test')
#    update.message.reply_audio(audio=open('records/0.wav','rb'))

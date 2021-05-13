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

# Moving servo via telegram bot
def move(update, context):
	message = update.message.text.split(' ')
	if len(message) < 3:
		update.message.reply_text('Write: \move horizontal|vertical numeric_value')
	if message[1] == 'horizontal':
		try:
			pos = int(message[2])
			pos = max([min([pos,600]),110])
			horizontal_mvt(pos)
		except:
			update.message.reply_text('Insert a valid number')
	elif message[1] == 'vertical':
		try:
			pos = int(message[2])
			pos = max([min([pos,280]),120])
			vertical_mvt(pos)
		except:
			update.message.reply_text('Insert a valid number')
	else:
		update.message.reply_text('Write: \move horizontal|vertical numeric_value')


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
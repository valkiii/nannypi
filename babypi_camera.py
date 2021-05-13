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
from utils import *

FORMAT = pyaudio.paInt16
config = configparser.ConfigParser()
config.read('settings.ini')

Threshold = 20

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024

CHANNELS = 1
RATE = 16000
swidth = 2

TIMEOUT_LENGTH = 3

f_name_directory = 'records/'

class Recorder():

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self,bot):
        self.bot = bot
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self):
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):
        n_files = len(os.listdir(f_name_directory))
        try:
            os.remove(filename)
        except:
            dummy=1

        filename = os.path.join(f_name_directory, '{}.wav'.format(n_files))

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        
        print('Written to file: {}'.format(filename))
        print('Sending file via Telegram Bot')
        for chat_id in config['DEFAULT']['AllowedUsers']:
            self.bot.send_audio(chat_id=chat_id,audio=open('records/0.wav','rb'))
        print('Removing file')
        os.remove(filename)
        print('Returning to listening')

    def listen(self):
        print('Listening beginning')
        while True:
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.record()

def main():
    
	updater = Updater(config['DEFAULT']['Token'], use_context=True)
	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("help", help))
	dispatcher.add_handler(CommandHandler("picture", send_picture))
	dispatcher.add_handler(CommandHandler("start_streaming", start_streaming))
	dispatcher.add_handler(CommandHandler("stop_streaming", stop_streaming))
	dispatcher.add_handler(CommandHandler("move", move))
	#dispatcher.add_handler(MessageHandler(Filters.text, text))
	updater.start_polling()
	bot = dispatcher.bot
	a = Recorder(bot)
	a.listen()
	updater.idle()


if __name__ == '__main__':
    main()

# !/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function

"""
说明：1 for -
0 for .

规则：滴=1t，嗒=3t，滴嗒间=1t，字符间=3t，单词间=7t
"""

from PyQt5.QtWidgets import QApplication
# from interface import Morse_interface
import datetime, sys
import pygame
import threading
import wave
import interface
import _thread
from sys import byteorder
from array import array
from struct import pack
import pyaudio
import time
import struct
import sys
import numpy as np

letter_to_morse = {
    "A": ".-", "B": "-...", "C": "-.-.",
    "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..",
    "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---",
    "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-",
    "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "1": ".----",
    "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.", "0": "-----",
    " ": "-..-."}
# Morse dictionnairy.
# from morse_dict import *
morse_dict = {
    "A": "01", "B": "1000", "C": "1010",
    "D": "100", "E": "0", "F": "0010",
    "G": "110", "H": "0000", "I": "00",
    "J": "0111", "K": "101", "L": "0100",
    "M": "11", "N": "10", "O": "111",
    "P": "0110", "Q": "1101", "R": "010",
    "S": "000", "T": "1", "U": "001",
    "V": "0001", "W": "011", "X": "1001",
    "Y": "1011", "Z": "1100", "1": "01111",
    "2": "00111", "3": "00011", "4": "00001",
    "5": "00000", "6": "10000", "7": "11000",
    "8": "11100", "9": "11110", "0": "11111",
    " ": "10010"}

T = 100  # 毫秒
T3 = 3 * T  # 单位：毫秒
THRESHOLD = 800  # 阈值
CHUNK = 160
FORMAT = pyaudio.paInt16
RATE = 16000  # 采样率
window = np.blackman(CHUNK)  # blackman窗
FREQ = 770  # 700HZ
HzVARIANCE = 200
SCAMPLE_TIME_ONE_TIME = CHUNK * 1000 / RATE  # 每次采样时间 计算结果：10毫秒
CHAR_INTERVAL = 200  # 字符间=3T
stringout = ""
change = 0

num_silent = 0

timelist = ""
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
stream.stop_stream()

# 单位：毫秒
def my_sleep(sleeptime):
    begin = datetime.datetime.now()

    while True:
        end = datetime.datetime.now()
        k = end - begin

        if (k.total_seconds() * 1000) > sleeptime:
            break


def play_sound(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while 1:
        if not pygame.mixer.music.get_busy():
            break


def long_pulse(is_sleep):
    play_sound("./audio/long.wav")

    if is_sleep == True:
        my_sleep(100)


def short_pulse(is_sleep):
    play_sound("./audio/short.wav")

    if is_sleep == True:
        my_sleep(100)


def gap_1t():
    # time.sleep(0.1)
    my_sleep(100)


def gap_3t():
    print("   ", end="")  # short gap
    # time.sleep(0.3)
    my_sleep(300)


def gap_7t():
    print("       ", end="\n")  # long gap
    # time.sleep(0.7)
    my_sleep(700)


def play_morse_code(morse_code):
    length = len(morse_code)
    for i in range(len(morse_code)):
        if morse_code[i] == '1':
            if i != length - 1:
                long_pulse(True)
            else:
                long_pulse(False)

        elif morse_code[i] == '0':
            if i != length - 1:
                short_pulse(True)
            else:
                short_pulse(False)


def play_text(alpha_text):
    print("\n===================\nPlaying\n===================\n")
    alpha_text = [item.upper() for item in alpha_text]  # alpha_text.upper()
    print(alpha_text)
    for letter in alpha_text:
        print(letter)
        if letter in morse_dict.keys():
            morse_code = morse_dict[letter]
            play_morse_code(morse_code)
            print("   ", morse_code)
            gap_3t()
        elif letter == " ":
            gap_7t()
        else:
            print("?", end="")
            sys.stdout.flush()
            gap_3t()

    print("\n")


def is_silent(sound_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(sound_data) < THRESHOLD


# important
# 正常情况是字符
def encode(raw_data):
    global stringout
    global change
    listascii = ""
    maximum = 0
    icount = 0

    # 过滤非电报音

    for i in range(len(raw_data)):
        if raw_data[i] == '1':
            icount += 1
            maximum = max(maximum, icount)
        elif raw_data[i] == '0':
            icount = 0

    if maximum < 5:
        print("\n--------throw it--------\n")
        return

    # 打印原始数据
    print("raw data:",raw_data)
    # 消除噪音(1/2)：消除干扰'1'
    i = 0
    j = 0
    temp_list = list(raw_data)
    while i < len(temp_list):
        if temp_list[i] == '0':
            i += 1
            continue

        for j in range(i, len(temp_list)):
            if temp_list[j] != temp_list[i]:
                break

        #
        if j - i <= 5 and temp_list[i-2] !='1' and temp_list[j+1]!='1':
        # if j-i<=5:
            for k in range(i, j):
                temp_list[k] = '0'
        else:
            i = j

        i += 1
    # make_one=0
    raw_data = ''.join(temp_list)
    temp_list = list(raw_data)
    print(raw_data)
    i = 0
    j = 0
    while i < len(temp_list):
        if temp_list[i] == '1':
            i += 1
            continue

        for j in range(i, len(temp_list)):
            # print(i,"%",j)
            if temp_list[j] != temp_list[i]:
                break

        #
        if j - i <= 5 and (temp_list[j + 1] == '1' and (temp_list[i - 2] == '1')):
        # if j-i<=5:
            for k in range(i, j):
                # print(i,"%",j)
                temp_list[k] = '1'
        else:
            i = j

        i += 1
    raw_data = ''.join(temp_list)
    print(raw_data);

    # 消除噪音(1/2)：消除干扰'0'

    temp_raw_data = raw_data[0]
    last_number = raw_data[0]
    for i in range(1, len(raw_data)):
        if raw_data[i] != last_number:
            temp_raw_data += '#'
            last_number = raw_data[i]
        temp_raw_data += raw_data[i]

    print("temp_raw_data",temp_raw_data)
    # print("\n")
    list1 = temp_raw_data.split("#")

    # print("\n-------modified data-------\n")
    print(list1)
    # print("\n-------modified data-------\n")
    # 生成嘀嗒序列
    for i in range(len(list1)):
        line = list1[i]
        if line[0] == '1':
            if len(list1[i]) >= 17 and len(list1[i]) < 100:  # 200-1000 ms dah, throws values > 100
                listascii += "-"
            elif len(list1[i]) < 17 and len(list1[i]) > 5:  # 50-200ms is dit
                listascii += "."

        if line[0] == '0':
            if len(list1[i]) >= 20 and len(list1[i]) < 60:  # 200-600 ms 字符间隔
                listascii += "#"

    listascii = listascii.split("#")
    print(listascii)
    listascii = [i for i in listascii if (len(str(i)) != 0)]
    # print("\n-------dida data-------\n")
    # print(listascii)
    # print("\n-------dida data-------\n")

    stringout = ""

    for i in range(len(listascii)):
        bFind = False
        for letter, morse in letter_to_morse.items():
            if listascii[i] == morse:
                stringout += letter
                bFind = True
        if bFind == False:
            print(listascii[i])
            stringout += '?'

    if stringout != "":
        print(stringout, end="")
        change = 1
        sys.stdout.flush()


def record(state):
    # 如果正在进行译码
    if state:
        global timelist
        global num_silent
        # print("##############START##############")

        stream.start_stream()
        sound_data = stream.read(CHUNK, exception_on_overflow=False)
        #print(sound_data)
        if byteorder == 'big':
            sound_data.byteswap()

        # r.extend(sound_data)
        sample_width = p.get_sample_size(FORMAT)

        # find frequency of each chunk
        indata = np.array(wave.struct.unpack("%dh" % (CHUNK), sound_data)) * window

        # take fft and square each value
        fftData = abs(np.fft.rfft(indata)) ** 2  # 取模
        which = fftData[1:].argmax() + 1  #
        silent = is_silent(indata)
        # signal frequency
        if silent:
            thefreq = 0
        elif which != len(fftData) - 1:
            y0, y1, y2 = np.log(fftData[which - 1:which + 2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            # find the frequency and output it
            thefreq = (which + x1) * RATE / CHUNK
            # print(thefreq)
        else:
            thefreq = which * RATE / CHUNK
            # print(thefreq)
        print(thefreq)
        # check frequency
        # if thefreq > (FREQ-HzVARIANCE) and thefreq < (FREQ+HzVARIANCE):
        if thefreq > 720 and thefreq < 820:
            # if which == 1:
            timelist += "1"
            num_silent = 0
        else:
            timelist += "0"
            num_silent += 1
            # print("0")

        if num_silent * SCAMPLE_TIME_ONE_TIME >= CHAR_INTERVAL and "1" in timelist:
            encode(timelist)
            timelist = ""

        # 10秒内无声，进行复位
        if num_silent * SCAMPLE_TIME_ONE_TIME > 10 * 1000:
            print("\n")
            print("reset")
            num_silent = 0
            timelist = ""

    # 如果不在进行译码
    if state == 0:
        num_silent = 0
        timelist = ""
        stream.stop_stream()

# 传递译码内容
def get_string():
    # print(stringout,'-----------------------')
    global change
    if change:
        change = 0
        return stringout
    else:
        return ''


# def main():

if __name__ == "__main__":
    pygame.mixer.init()
    pygame.time.delay(300)  # 等待0.3秒让mixer完成初始化

    app = QApplication(sys.argv)
    w = interface.Morse_interface()
    sys.exit(app.exec_())

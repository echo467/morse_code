# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import morse
import pygame
import threading
import _thread
import button_image_rc
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QDesktopWidget
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtCore import QTimer
import importlib

class Morse_interface(QWidget):
    def __init__(self):
        super(Morse_interface, self).__init__()
        self.init_ui()
        self.show()
        self.start_end_time=0
        self.pause_continue_time=0
        self.state=0
        self.clean=0
        self.text=""

    #初始化UI界面
    def init_ui(self):
        self.init_window()
        self.init_Button()

        #每毫秒检测一次译码状态
        record_time = QTimer(self)
        record_time.setInterval(10)
        record_time.timeout.connect(lambda:self.record_decode())
        record_time.start()

    #初始化界面大小，标题和logo
    def init_window(self):
        self.resize(459, 364)
        self.setMinimumSize(459, 364)
        self.setMaximumSize(459, 364)
        self.setWindowTitle('摩尔斯编译码')
        self.setWindowIcon(QIcon(':/images/icon.png'))
        #background_time = QTimer(self)
        #background_time.setInterval(1)
        #background_time.timeout.connect(lambda:self.init_background())
        #background_time.start()
    '''
    def init_background(self):
        self.setAutoFillBackground(True)
        palette = QPalette()
        #palette.setBrush(QPalette.Background, QBrush(QPixmap("./timg.png").scaled(self.size(),Qt.IgnoreAspectRatio,Qt.SmoothTransformation)))
        self.setPalette(palette)'''

    def init_Button(self):
        #开始编码
        self.encodeButton = QtWidgets.QPushButton(self)
        self.encodeButton.setGeometry(QtCore.QRect(320, 60, 81, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.encodeButton.setFont(font)
        self.encodeButton.setObjectName("encodeButton")
        self.encodeButton.clicked.connect(self.get_user_text)

        #开始/结束译码
        self.start_end_Button = QtWidgets.QPushButton(self)
        self.start_end_Button.setGeometry(QtCore.QRect(315, 210, 71, 64))
        self.start_end_Button.setStyleSheet("background:transparent;")
        self.start_end_Button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/images/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.start_end_Button.setIcon(icon)
        self.start_end_Button.setIconSize(QtCore.QSize(64, 64))
        self.start_end_Button.setObjectName("start_end_Button")
        self.start_end_Button.setCheckable(True)
        self.start_end_Button.setFlat(True)
        self.start_end_Button.clicked.connect(self.start_end_click)

        #暂停/继续译码
        self.pause_continue_Button = QtWidgets.QPushButton(self)
        self.pause_continue_Button.setGeometry(QtCore.QRect(380, 210, 71, 64))
        self.pause_continue_Button.setStyleSheet("background:transparent;")
        self.pause_continue_Button.setText("")
        self.pause_continue_Button.setIconSize(QtCore.QSize(64, 64))
        self.pause_continue_Button.setObjectName("pause_continue_radioButton")
        icon_2 = QtGui.QIcon()
        icon_2.addPixmap(QtGui.QPixmap(":/images/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon_2.addPixmap(QtGui.QPixmap(":/images/start.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pause_continue_Button.setIcon(icon_2)
        self.pause_continue_Button.setCheckable(True)
        self.pause_continue_Button.setEnabled(False)
        self.pause_continue_Button.setFlat(True)
        self.pause_continue_Button.clicked.connect(self.pause_continue_click)

        #分割线
        self.splitLine = QtWidgets.QLabel(self)
        self.splitLine.setGeometry(QtCore.QRect(20, 120, 431, 20))
        self.splitLine.setObjectName("splitLine")

        #获取编码内容
        self.imputMessage_lineEdit = QtWidgets.QLineEdit(self)
        self.imputMessage_lineEdit.setGeometry(QtCore.QRect(40, 60, 261, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.imputMessage_lineEdit.setFont(font)
        self.imputMessage_lineEdit.setObjectName("imputMessage_lineEdit")

        #提示输入编码内容文本框
        self.Please_type_your_message = QtWidgets.QLabel(self)
        self.Please_type_your_message.setGeometry(QtCore.QRect(40, 30, 250, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        self.Please_type_your_message.setFont(font)
        self.Please_type_your_message.setObjectName("Please_type_your_message")

        #显示译码内容提示窗
        self.showMessage_textBrowser = QtWidgets.QTextBrowser(self)
        self.showMessage_textBrowser.setGeometry(QtCore.QRect(40, 200, 261, 81))
        self.showMessage_textBrowser.setObjectName("showMessage_textBrowser")

        #显示译码内容
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 170, 280, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")

        #翻译界面文字
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.encodeButton.setText(_translate("Form", "encode"))
        self.splitLine.setText(_translate("Form", "--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--"))
        self.Please_type_your_message.setText(_translate("Form", "Please type your message:"))
        self.label.setText(_translate("Form", "Show the recieved message:"))

    #获取输入编码内容并进行编码
    def get_user_text(self):
        user_text = self.imputMessage_lineEdit.text()
        user_text = user_text.lower()
        word_list = list(user_text)
        morse.play_text(word_list)

    #开始结束按钮触发函数
    def start_end_click(self):
        if self.start_end_time==0:
            self.start_end_time=1
            self.pause_continue_Button.setEnabled(True)
            self.pause_continue_time=0
            self.state=1
            self.clean=0
        else:
            self.pause_continue_Button.setEnabled(False)
            self.start_end_time = 0
            self.clean=1
            if self.pause_continue_time%2==0:
                self.state=0
            else:
                self.pause_continue_time = 0
                self.pause_continue_Button.setChecked(False)

    #暂停继续按钮触发函数
    def pause_continue_click(self):
        if self.pause_continue_time==0:
            self.pause_continue_time=1
            self.state=0
        else:
            self.pause_continue_time = 0
            self.state=1

    #译码函数
    def record_decode(self):
        if self.state==1:
            morse.record(1)

            if self.clean==0:
                self.text+=morse.get_string()
            else:
                self.text=""
            self.showMessage_textBrowser.setText(self.text)
        else:
            morse.record(0)
            self.showMessage_textBrowser.setText('')
            self.text=''
            importlib.reload(morse)

if __name__ == "__main__":
    pygame.mixer.init()
    pygame.time.delay(300)   #等待0.3秒让mixer完成初始化

    app = QApplication(sys.argv)
    w = Morse_interface()

    sys.exit(app.exec_())
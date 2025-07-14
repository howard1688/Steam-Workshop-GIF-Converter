from moviepy.video.io.VideoFileClip import VideoFileClip
import selenium.webdriver.edge.options
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import cv2
import os
from PIL import Image
from PIL import ImageSequence
import time
import traceback
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        font = QtGui.QFont("Microsoft JhengHei", 10)
        self.setFont(font)
        self.retranslateUi(self)
        self.init_slots()
        self.video_path = ''   # 影片路徑
        self.init_timer()
        self.cap = cv2.VideoCapture()
        self.start_time = 0
        self.finish_time = 0
        self.video_fps = 0

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(505, 530)
        MainWindow.setMinimumSize(QtCore.QSize(505, 530))
        MainWindow.setMaximumSize(QtCore.QSize(505, 530))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(57, 17, 389, 227))
        self.label.setStyleSheet("")
        self.label.setText("")
        self.label.setObjectName("label")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 270, 481, 32))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(90, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.textEdit = QtWidgets.QTextEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setMinimumSize(QtCore.QSize(300, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout.addWidget(self.textEdit)
        self.toolButtonInput = QtWidgets.QToolButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButtonInput.sizePolicy().hasHeightForWidth())
        self.toolButtonInput.setSizePolicy(sizePolicy)
        self.toolButtonInput.setMinimumSize(QtCore.QSize(40, 30))
        self.toolButtonInput.setMaximumSize(QtCore.QSize(16777215, 30))
        self.toolButtonInput.setObjectName("toolButtonInput")
        self.horizontalLayout.addWidget(self.toolButtonInput)
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(310, 350, 181, 32))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget_2)
        self.pushButton.setMinimumSize(QtCore.QSize(50, 30))
        self.pushButton.setMaximumSize(QtCore.QSize(50, 30))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_fixgif = QtWidgets.QPushButton(self.layoutWidget_2)
        self.pushButton_fixgif.setMinimumSize(QtCore.QSize(70, 30))
        self.pushButton_fixgif.setMaximumSize(QtCore.QSize(70, 30))
        self.pushButton_fixgif.setObjectName("pushButton_fixgif")
        self.horizontalLayout_2.addWidget(self.pushButton_fixgif)      
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget_2)
        self.pushButton_2.setMinimumSize(QtCore.QSize(50, 30))
        self.pushButton_2.setMaximumSize(QtCore.QSize(50, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.label_template = QtWidgets.QLabel(self.centralwidget)
        self.label_template.setGeometry(QtCore.QRect(50, 10, 403, 241))
        self.label_template.setText("")
        self.label_template.setObjectName("label_template")
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 310, 481, 32))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(130, 30))
        self.label_6.setMaximumSize(QtCore.QSize(130, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        self.time_start = QtWidgets.QTextEdit(self.layoutWidget1)
        self.time_start.setMinimumSize(QtCore.QSize(35, 0))
        self.time_start.setMaximumSize(QtCore.QSize(35, 30))
        self.time_start.setObjectName("time_start")
        self.horizontalLayout_3.addWidget(self.time_start)
        self.label_11 = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setMinimumSize(QtCore.QSize(5, 30))
        self.label_11.setMaximumSize(QtCore.QSize(5, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_3.addWidget(self.label_11)
        self.time_start_2 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.time_start_2.setMinimumSize(QtCore.QSize(35, 0))
        self.time_start_2.setMaximumSize(QtCore.QSize(35, 30))
        self.time_start_2.setObjectName("time_start_2")
        self.horizontalLayout_3.addWidget(self.time_start_2)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QtCore.QSize(30, 30))
        self.label_7.setMaximumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.time_finish = QtWidgets.QTextEdit(self.layoutWidget1)
        self.time_finish.setMinimumSize(QtCore.QSize(35, 0))
        self.time_finish.setMaximumSize(QtCore.QSize(35, 30))
        self.time_finish.setObjectName("time_finish")
        self.horizontalLayout_3.addWidget(self.time_finish)
        self.label_12 = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setMinimumSize(QtCore.QSize(5, 30))
        self.label_12.setMaximumSize(QtCore.QSize(5, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_3.addWidget(self.label_12)
        self.time_finish_2 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.time_finish_2.setMinimumSize(QtCore.QSize(35, 0))
        self.time_finish_2.setMaximumSize(QtCore.QSize(35, 30))
        self.time_finish_2.setObjectName("time_finish_2")
        self.horizontalLayout_3.addWidget(self.time_finish_2)
        spacerItem = QtWidgets.QSpacerItem(50, 30, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox.setMinimumSize(QtCore.QSize(100, 30))
        self.checkBox.setMaximumSize(QtCore.QSize(100, 30))
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_3.addWidget(self.checkBox)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 350, 281, 32))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_8 = QtWidgets.QLabel(self.layoutWidget2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMinimumSize(QtCore.QSize(130, 30))
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_4.addWidget(self.label_8)
        self.output_name = QtWidgets.QTextEdit(self.layoutWidget2)
        self.output_name.setMinimumSize(QtCore.QSize(0, 30))
        self.output_name.setMaximumSize(QtCore.QSize(16777215, 30))
        self.output_name.setObjectName("output_name")
        self.horizontalLayout_4.addWidget(self.output_name)
        self.layoutWidget3 = QtWidgets.QWidget(self.centralwidget)
        # FPS 設定欄位
        self.layoutWidget_fps = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_fps.setGeometry(QtCore.QRect(10, 390, 350, 32))
        self.layoutWidget_fps.setObjectName("layoutWidget_fps")
        self.horizontalLayout_fps = QtWidgets.QHBoxLayout(self.layoutWidget_fps)
        self.horizontalLayout_fps.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_fps.setSpacing(5)
        self.horizontalLayout_fps.setObjectName("horizontalLayout_fps")

        self.label_fps = QtWidgets.QLabel(self.layoutWidget_fps)
        self.label_fps.setMinimumSize(QtCore.QSize(50, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_fps.setFont(font)
        self.label_fps.setObjectName("label_fps")
        self.horizontalLayout_fps.addWidget(self.label_fps)

        self.horizontalLayout_fps.setSpacing(2)
        self.fps_input = QtWidgets.QTextEdit(self.layoutWidget_fps)
        self.fps_input.setMinimumSize(QtCore.QSize(50, 30))
        self.fps_input.setMaximumSize(QtCore.QSize(50, 30))
        self.fps_input.setObjectName("fps_input")
        self.fps_input.setText("10")
        self.horizontalLayout_fps.addWidget(self.fps_input)

        self.label_fps_note = QtWidgets.QLabel(self.layoutWidget_fps)
        self.label_fps_note.setMinimumSize(QtCore.QSize(120, 30))
        self.label_fps_note.setText("※越小播放越快，預設10fps")
        self.label_fps_note.setObjectName("label_fps_note")
        self.horizontalLayout_fps.addWidget(self.label_fps_note)
        self.layoutWidget3.setGeometry(QtCore.QRect(10, 430, 481, 32))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

    
        self.label_9 = QtWidgets.QLabel(self.layoutWidget3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QtCore.QSize(70, 30))
        self.label_9.setMaximumSize(QtCore.QSize(70, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_5.addWidget(self.label_9)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget3)
        self.comboBox.setMinimumSize(QtCore.QSize(80, 30))
        self.comboBox.setMaximumSize(QtCore.QSize(80, 30))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_5.addWidget(self.comboBox)
        self.label_10 = QtWidgets.QLabel(self.layoutWidget3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setMinimumSize(QtCore.QSize(100, 30))
        self.label_10.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_5.addWidget(self.label_10)
        self.workshop_name = QtWidgets.QTextEdit(self.layoutWidget3)
        self.workshop_name.setMinimumSize(QtCore.QSize(0, 30))
        self.workshop_name.setMaximumSize(QtCore.QSize(100, 30))
        self.workshop_name.setObjectName("workshop_name")
        self.horizontalLayout_5.addWidget(self.workshop_name)
        self.pushButton_3 = QtWidgets.QPushButton(self.layoutWidget3)
        self.pushButton_3.setMinimumSize(QtCore.QSize(70, 30))
        self.pushButton_3.setMaximumSize(QtCore.QSize(70, 30))
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_5.addWidget(self.pushButton_3)
        
        # 新增上傳gif的選項
        self.layoutWidget_upload = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_upload.setGeometry(QtCore.QRect(10, 470, 481, 32))
        self.layoutWidget_upload.setObjectName("layoutWidget_upload")
        self.horizontalLayout_upload = QtWidgets.QHBoxLayout(self.layoutWidget_upload)
        self.horizontalLayout_upload.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_upload.setObjectName("horizontalLayout_upload")
        
        # 標籤
        self.label_upload = QtWidgets.QLabel(self.layoutWidget_upload)
        self.label_upload.setMinimumSize(QtCore.QSize(90, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_upload.setFont(font)
        self.label_upload.setObjectName("label_upload")
        self.horizontalLayout_upload.addWidget(self.label_upload)
        
        # 全部選項
        self.checkBox_all = QtWidgets.QCheckBox(self.layoutWidget_upload)
        self.checkBox_all.setMinimumSize(QtCore.QSize(50, 30))
        self.checkBox_all.setObjectName("checkBox_all")
        self.checkBox_all.setChecked(True)  # 預設選中全部
        self.horizontalLayout_upload.addWidget(self.checkBox_all)
        
        # 1-5選項
        self.checkBox_part1 = QtWidgets.QCheckBox(self.layoutWidget_upload)
        self.checkBox_part1.setMinimumSize(QtCore.QSize(30, 30))
        self.checkBox_part1.setObjectName("checkBox_part1")
        self.horizontalLayout_upload.addWidget(self.checkBox_part1)
        
        self.checkBox_part2 = QtWidgets.QCheckBox(self.layoutWidget_upload)
        self.checkBox_part2.setMinimumSize(QtCore.QSize(30, 30))
        self.checkBox_part2.setObjectName("checkBox_part2")
        self.horizontalLayout_upload.addWidget(self.checkBox_part2)
        
        self.checkBox_part3 = QtWidgets.QCheckBox(self.layoutWidget_upload)
        self.checkBox_part3.setMinimumSize(QtCore.QSize(30, 30))
        self.checkBox_part3.setObjectName("checkBox_part3")
        self.horizontalLayout_upload.addWidget(self.checkBox_part3)
        
        self.checkBox_part4 = QtWidgets.QCheckBox(self.layoutWidget_upload)
        self.checkBox_part4.setMinimumSize(QtCore.QSize(30, 30))
        self.checkBox_part4.setObjectName("checkBox_part4")
        self.horizontalLayout_upload.addWidget(self.checkBox_part4)
        
        self.checkBox_part5 = QtWidgets.QCheckBox(self.layoutWidget_upload)
        self.checkBox_part5.setMinimumSize(QtCore.QSize(30, 30))
        self.checkBox_part5.setObjectName("checkBox_part5")
        self.horizontalLayout_upload.addWidget(self.checkBox_part5)
        
        # 調整主視窗大小以容納新增元素
        MainWindow.resize(505, 580)
        MainWindow.setMinimumSize(QtCore.QSize(505, 580))
        MainWindow.setMaximumSize(QtCore.QSize(505, 580))
        
        # 新增進度條
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 510, 481, 25))
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)  # 初始隱藏
        
        # 進度標籤
        self.label_progress = QtWidgets.QLabel(self.centralwidget)
        self.label_progress.setGeometry(QtCore.QRect(10, 540, 481, 20))
        self.label_progress.setObjectName("label_progress")
        self.label_progress.setText("準備中...")
        self.label_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.label_progress.setVisible(False)  # 初始隱藏
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 505, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_5.setText(_translate("MainWindow", "影片路徑："))
        self.toolButtonInput.setText(_translate("MainWindow", "..."))
        self.pushButton.setText(_translate("MainWindow", "切片"))
        self.pushButton_2.setText(_translate("MainWindow", "關閉"))
        self.pushButton_fixgif.setText(_translate("MainWindow", "3B尾改21"))
        self.label_6.setText(_translate("MainWindow", "選擇影片時長：從"))
        self.label_11.setText(_translate("MainWindow", "："))
        self.label_7.setText(_translate("MainWindow", " 到"))
        self.label_12.setText(_translate("MainWindow", "："))
        self.checkBox.setText(_translate("MainWindow", "播放影片"))
        self.label_8.setText(_translate("MainWindow", "輸出的切片名稱："))
        self.label_9.setText(_translate("MainWindow", "瀏覽器："))
        self.comboBox.setItemText(0, _translate("MainWindow", "Edge"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Chrome"))
        self.label_10.setText(_translate("MainWindow", "工作坊名稱："))
        self.pushButton_3.setText(_translate("MainWindow", "上傳"))
        self.label_fps.setText(_translate("MainWindow", "設定gif的幀率："))
        self.label_fps_note.setText(_translate("MainWindow", "※越小播放越快，預設10fps"))
        self.label_upload.setText(_translate("MainWindow", "選擇上傳gif："))
        self.checkBox_all.setText(_translate("MainWindow", "全部"))
        self.checkBox_part1.setText(_translate("MainWindow", "1"))
        self.checkBox_part2.setText(_translate("MainWindow", "2"))
        self.checkBox_part3.setText(_translate("MainWindow", "3"))
        self.checkBox_part4.setText(_translate("MainWindow", "4"))
        self.checkBox_part5.setText(_translate("MainWindow", "5"))

    def init_slots(self):
        self.pushButton.clicked.connect(self.split_video_to_gifs)  # 連接切片函數
        self.time_start.textChanged.connect(self.read_time_start)
        self.time_start_2.textChanged.connect(self.read_time_start)
        self.time_finish.textChanged.connect(self.read_time_finish)
        self.time_finish_2.textChanged.connect(self.read_time_finish)
        self.toolButtonInput.clicked.connect(self.InpurDir)           # 連接影片路徑選擇函數
        self.pushButton_3.clicked.connect(self.upload_gif)
        # self.toolButtonOutput.clicked.connect(self.SaveResults)
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton_fixgif.clicked.connect(self.fix_gif_trailer)
        pix = QPixmap('template_1.png')        # 設置label圖片
        self.label_template.setPixmap(pix)
        self.label_template.setScaledContents(True)  # 自適應QLabel大小
        self.output_name.setPlainText("output_gif")
        self.workshop_name.setText('gif') # 設置上傳名稱

        self.checkBox.setChecked(True)
        self.checkBox.clicked.connect(self.check_video_play)
        
        # 綁定上傳勾選框的信號
        self.checkBox_all.clicked.connect(self.on_all_checkbox_clicked)
        self.checkBox_part1.clicked.connect(self.on_part_checkbox_clicked)
        self.checkBox_part2.clicked.connect(self.on_part_checkbox_clicked)
        self.checkBox_part3.clicked.connect(self.on_part_checkbox_clicked)
        self.checkBox_part4.clicked.connect(self.on_part_checkbox_clicked)
        self.checkBox_part5.clicked.connect(self.on_part_checkbox_clicked)

    def InpurDir(self):
        try:
            video_type = [".mp4", ".mkv", ".MOV", ".avi", ".m4v"]
            file_dialog = QtWidgets.QFileDialog.getOpenFileName(
                self, 
                "選擇影片檔案", 
                "", 
                "影片檔案 (*.mp4 *.mkv *.MOV *.avi *.m4v);;所有檔案(*.*)"
            )
            self.video_path = file_dialog[0]

            # 檢查是否選擇了檔案
            if not self.video_path:
                return

            # 檢查檔案是否存在
            if not os.path.exists(self.video_path):
                QtWidgets.QMessageBox.warning(self, "錯誤", "檔案不存在", QtWidgets.QMessageBox.Yes)
                return

            # 檢查檔案大小
            file_size = os.path.getsize(self.video_path)
            if file_size == 0:
                QtWidgets.QMessageBox.warning(self, "錯誤", "檔案內容為空檔案", QtWidgets.QMessageBox.Yes)
                return

            # 判斷是否為支援的影片格式
            is_supported = False
            for vdi in video_type:
                if vdi.lower() in self.video_path.lower():
                    is_supported = True
                    break
            
            if not is_supported:
                QtWidgets.QMessageBox.warning(self, "格式錯誤", 
                    f"不支援該格式！\n支援格式：{', '.join(video_type)}", 
                    QtWidgets.QMessageBox.Yes)
                return

            print("選擇輸入影片路徑", self.video_path)
            self.textEdit.setPlainText(self.video_path)
            print("videoIsOpen")

            # 計算影片長度,並設置滑動軸中時間
            try:
                duration = self.get_video_duration()
                if duration <= 0:
                    QtWidgets.QMessageBox.warning(self, "錯誤", "無法讀取影片時長，請檢查影片檔案", QtWidgets.QMessageBox.Yes)
                    return
                    
                self.time_start.setText("00")
                self.time_start_2.setText("00")
                if duration < 15:
                    self.finish_time = duration
                    self.time_finish.setText("00")
                    self.time_finish_2.setText(str(duration))
                else:
                    self.finish_time = 10
                    self.time_finish.setText("00")
                    self.time_finish_2.setText("10")

                # 嘗試開啟影片預覽
                if self.cap.isOpened():
                    self.cap.release()
                
                self.cap.open(self.video_path)
                if not self.cap.isOpened():
                    QtWidgets.QMessageBox.warning(self, "警告", "無法開啟影片預覽，但可以繼續處理", QtWidgets.QMessageBox.Yes)
                else:
                    self.timer.start(30)   # 設置影片播放計時器                    
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "錯誤", f"讀取影片時發生錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
                return
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "系統錯誤", f"選擇檔案時發生未預期錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
            print(f"InpurDir error: {traceback.format_exc()}")

    def get_video_duration(self):
        video = cv2.VideoCapture(self.video_path)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = video.get(cv2.CAP_PROP_FPS)
        self.video_fps = int(frame_rate)               # 更新影片幀率
        print("fps:", self.video_fps)
        duration = int(frame_count / frame_rate)
        video.release()
        return duration

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_video)

    def check_video_play(self):
        if self.checkBox.isChecked():
            self.timer.start(30)
            print("play video")
        else:
            self.timer.stop()
            print("pause video")

    def play_video(self):
        ret, img = self.cap.read()
        if ret:
            # 影片流轉換為RGB
            height, width = img.shape[:2]
            # 對影片進行縮放適應label大小
            cur_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            pixmap = QImage(cur_frame, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(pixmap)
            self.label.setScaledContents(True)
            # 影片流置於label中間播放
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setPixmap(pixmap)

    def read_time_start(self):
        try:
            if ":" in self.time_start.toPlainText():
                print("minite")
            else:
                # 驗證輸入是否為數字
                minute_text = self.time_start.toPlainText().strip()
                second_text = self.time_start_2.toPlainText().strip()
                
                if minute_text and not minute_text.isdigit():
                    self.time_start.setPlainText("00")
                    QtWidgets.QMessageBox.warning(self, "輸入錯誤", "分鐘必須為數字", QtWidgets.QMessageBox.Yes)
                    return
                    
                if second_text and not second_text.isdigit():
                    self.time_start_2.setPlainText("00")
                    QtWidgets.QMessageBox.warning(self, "輸入錯誤", "秒數必須為數字", QtWidgets.QMessageBox.Yes)
                    return
                
                # 檢查秒數是否超過59
                if second_text and int(second_text) > 59:
                    self.time_start_2.setPlainText("59")
                    QtWidgets.QMessageBox.warning(self, "輸入錯誤", "秒數不能超過59", QtWidgets.QMessageBox.Yes)
                    return
                
                print("start time:", self.time_start.toPlainText(),":", self.time_start_2.toPlainText())
        except Exception as e:
            print(f"read_time_start error: {e}")

    def read_time_finish(self):
        try:
            if ":" in self.time_finish.toPlainText():
                print("minite")
            else:
                # 驗證輸入是否為數字
                minute_text = self.time_finish.toPlainText().strip()
                second_text = self.time_finish_2.toPlainText().strip()
                
                if minute_text and not minute_text.isdigit():
                    self.time_finish.setPlainText("00")
                    QtWidgets.QMessageBox.warning(self, "輸入錯誤", "分鐘必須為數字", QtWidgets.QMessageBox.Yes)
                    return
                    
                if second_text and not second_text.isdigit():
                    self.time_finish_2.setPlainText("00")
                    QtWidgets.QMessageBox.warning(self, "輸入錯誤", "秒數必須為數字", QtWidgets.QMessageBox.Yes)
                    return
                
                # 檢查秒數是否超過59
                if second_text and int(second_text) > 59:
                    self.time_finish_2.setPlainText("59")
                    QtWidgets.QMessageBox.warning(self, "輸入錯誤", "秒數不能超過59", QtWidgets.QMessageBox.Yes)
                    return

                print("finish time:", self.time_finish.toPlainText(), ":", self.time_finish_2.toPlainText())
        except Exception as e:
            print(f"read_time_finish error: {e}")

    def split_video_to_gifs(self):
        try:
            # 檢查是否已選擇影片
            if not self.video_path or not os.path.exists(self.video_path):
                QtWidgets.QMessageBox.warning(self, "錯誤", "請先選擇有效的影片檔案", QtWidgets.QMessageBox.Yes)
                return
            
            # 檢查輸出名稱是否為空
            output_name = self.output_name.toPlainText().strip()
            if not output_name:
                QtWidgets.QMessageBox.warning(self, "錯誤", "請輸入輸出檔案名稱", QtWidgets.QMessageBox.Yes)
                return
            
            # 檢查檔案名稱是否包含非法字符
            invalid_chars = '<>:"/\\|?*'
            if any(char in output_name for char in invalid_chars):
                QtWidgets.QMessageBox.warning(self, "錯誤", f"檔案名稱不能包含以下字符：{invalid_chars}", QtWidgets.QMessageBox.Yes)
                return
            
            # 驗證時間輸入
            try:
                start_min = int(self.time_start.toPlainText() or "0")
                start_sec = int(self.time_start_2.toPlainText() or "0")
                finish_min = int(self.time_finish.toPlainText() or "0")
                finish_sec = int(self.time_finish_2.toPlainText() or "0")
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "錯誤", "時間必須為數字", QtWidgets.QMessageBox.Yes)
                return
            
            #計算時間
            self.start_time = start_min * 60 + start_sec
            self.finish_time = finish_min * 60 + finish_sec
            
            # 檢查時間邏輯
            if self.start_time >= self.finish_time:
                QtWidgets.QMessageBox.warning(self, "錯誤", "結束時間必須大於開始時間", QtWidgets.QMessageBox.Yes)
                return
            
            if self.finish_time - self.start_time < 1:
                QtWidgets.QMessageBox.warning(self, "錯誤", "影片片段至少1秒", QtWidgets.QMessageBox.Yes)
                return
            
            # 檢查FPS輸入
            try:
                fps_value = int(self.fps_input.toPlainText() or "10")
                if fps_value <= 0 or fps_value > 60:
                    fps_value = 10
                    self.fps_input.setPlainText("10")
                    QtWidgets.QMessageBox.warning(self, "FPS警告", "FPS值無效，已重新設為10", QtWidgets.QMessageBox.Yes)
            except ValueError:
                fps_value = 10
                self.fps_input.setPlainText("10")
                QtWidgets.QMessageBox.warning(self, "FPS錯誤", "FPS必須為數字，已重新設為10", QtWidgets.QMessageBox.Yes)

            # 開始處理影片
            print("開始處理影片...")
            
            # 檢查檔案大小，提前警告
            file_size_mb = os.path.getsize(self.video_path) / (1024 * 1024)
            print(f"影片檔案大小: {file_size_mb:.1f}MB")
            
            if file_size_mb > 50:  # 超過50MB
                reply = QtWidgets.QMessageBox.question(self, "大檔案提醒", 
                    f"影片檔案較大 ({file_size_mb:.1f}MB)，載入可能需要 10-30 秒。\n"
                    f"建議:\n"
                    f"• 縮短處理時間（如改為0-5秒）\n" 
                    f"• 或耐心等待載入完成\n\n"
                    f"是否繼續處理？", 
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    return
            
            # 顯示進度條
            self.progressBar.setVisible(True)
            self.label_progress.setVisible(True)
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(100)
            self.label_progress.setText(f"正在載入影片檔案 ({file_size_mb:.1f}MB)...")
            QtWidgets.QApplication.processEvents()  # 更新UI
            
            try:
                # 讀取影片檔案
                print(f"載入影片: {self.video_path}")
                
                # 嘗試載入影片，添加超時和錯誤處理
                try:
                    video = VideoFileClip(self.video_path)
                    self.progressBar.setValue(20)
                    self.label_progress.setText("影片載入完成")
                    QtWidgets.QApplication.processEvents()
                except Exception as load_error:
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.critical(self, "載入錯誤", 
                        f"無法載入影片檔案，可能的原因：\n"
                        f"1. 影片格式不支援\n"
                        f"2. 檔案損壞\n"
                        f"3. 編碼器問題\n"
                        f"4. 檔案太大，記憶體不足\n\n"
                        f"詳細錯誤：{str(load_error)}", 
                        QtWidgets.QMessageBox.Yes)
                    return
                
                # 檢查影片是否成功載入
                if video is None:
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.warning(self, "錯誤", "無法載入影片檔案", QtWidgets.QMessageBox.Yes)
                    return
                
                # 驗證影片基本屬性
                try:
                    duration = video.duration
                    size = video.size
                    fps = video.fps
                    print(f"影片載入成功，時長: {duration}秒, 尺寸: {size}, FPS: {fps}")
                    self.progressBar.setValue(30)
                    self.label_progress.setText(f"影片資訊讀取完成 - {duration:.1f}秒, {size}")
                    QtWidgets.QApplication.processEvents()
                except Exception as attr_error:
                    video.close()
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.warning(self, "錯誤", 
                        f"影片檔案資訊讀取失敗：{str(attr_error)}", 
                        QtWidgets.QMessageBox.Yes)
                    return
                
                # 檢查影片長度
                if video.duration < self.finish_time:
                    video.close()
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.warning(self, "錯誤", f"結束時間超過影片長度！影片總長度：{int(video.duration)}秒", QtWidgets.QMessageBox.Yes)
                    return
                
                # 裁剪影片時間段
                print(f"裁剪影片時間段: {self.start_time}秒 到 {self.finish_time}秒")
                self.progressBar.setValue(40)
                self.label_progress.setText(f"正在裁剪時間段: {self.start_time}-{self.finish_time}秒...")
                QtWidgets.QApplication.processEvents()
                video = video.subclipped(self.start_time, self.finish_time)
                if video is None:
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.warning(self, "錯誤", "影片時間裁剪失敗", QtWidgets.QMessageBox.Yes)
                    return

                # 縮放影片尺寸大小
                print("調整影片尺寸...")
                self.progressBar.setValue(50)
                self.label_progress.setText("正在調整影片尺寸...")
                QtWidgets.QApplication.processEvents()
                video = video.resized((770,449))
                if video is None:
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.warning(self, "錯誤", "影片尺寸調整失敗", QtWidgets.QMessageBox.Yes)
                    return

                # 獲取影片寬高
                width, height = video.size
                print(f"調整後尺寸: {width}x{height}")

                # 計算每個片段寬度（去除邊距後平均分配）
                segment_width = (width - 20) / 5
                print(f"每個片段寬度: {segment_width}")
                
                # 驗證尺寸參數
                if segment_width <= 0:
                    self.progressBar.setVisible(False)
                    self.label_progress.setVisible(False)
                    QtWidgets.QMessageBox.warning(self, "錯誤", "影片寬度太小，無法分割成5部分", QtWidgets.QMessageBox.Yes)
                    video.close()
                    return

                # 開始生成GIF
                self.progressBar.setValue(60)
                self.label_progress.setText("開始生成GIF檔案...")
                QtWidgets.QApplication.processEvents()

                for i in range(5):
                    print(f"正在處理第{i+1} 片段..")
                    
                    # 更新進度條 (60-90之間，每個片段佔6%)
                    progress_value = 60 + (i * 6)
                    self.progressBar.setValue(progress_value)
                    self.label_progress.setText(f"正在處理 part{i+1} ({i+1}/5)...")
                    QtWidgets.QApplication.processEvents()
                    
                    # 計算每個 GIF 的起始和結束位置
                    start_x = int(i * segment_width + i * 5)
                    end_x = int(start_x + segment_width)
                    
                    # 確保座標在有效範圍內
                    start_x = max(0, start_x)
                    end_x = min(width, end_x)
                    
                    # 檢查裁剪區域是否有效
                    if end_x <= start_x:
                        print(f"警告：part{i+1} 座標無效 (start_x={start_x}, end_x={end_x})，跳過此片段")
                        continue
                        
                    if end_x - start_x < 10:  # 最小寬度檢查
                        print(f"警告：part{i+1} 寬度太小 ({end_x - start_x}px)，跳過此片段")
                        continue
                    
                    print(f"Part{i+1} 裁剪範圍: x={start_x} 到 {end_x} (寬度: {end_x - start_x}px)")

                    # 裁剪影片
                    try:
                        print(f"開始裁剪 part{i+1}...")
                        print(f"  影片尺寸: {width}x{height}")
                        print(f"  裁剪座標: x1={start_x}, x2={end_x}, y1=0, y2={height}")
                        
                        # 再次驗證座標
                        if start_x < 0 or end_x > width or start_x >= end_x:
                            print(f"錯誤：part{i+1} 座標參數無效")
                            continue
                            
                        # 執行裁剪操作
                        gif_segment = video.cropped(x1=start_x, x2=end_x, y1=0, y2=height)
                        
                        # 詳細檢查裁剪結果
                        if gif_segment is None:
                            print(f"錯誤：part{i+1} 裁剪返回 None")
                            print("  可能原因：")
                            print("  1. MoviePy 版本相容性問題")
                            print("  2. 影片編碼格式問題")
                            print("  3. 記憶體不足")
                            continue
                            
                        # 檢查裁剪後的影片屬性
                        try:
                            segment_size = gif_segment.size
                            segment_duration = gif_segment.duration
                            print(f"Part{i+1} 裁剪成功，尺寸: {segment_size}, 時長: {segment_duration}秒")
                        except Exception as attr_error:
                            print(f"錯誤：part{i+1} 裁剪後屬性讀取失敗：{str(attr_error)}")
                            continue

                        # 輸出 GIF 檔案
                        output_file = f"{output_name}_part{i + 1}.gif"
                        print(f"正在輸出 {output_file}...")
                        
                        # 更新進度條到具體的GIF生成階段
                        gif_progress = 60 + (i * 6) + 3  # 每個GIF中間階段
                        self.progressBar.setValue(gif_progress)
                        self.label_progress.setText(f"正在生成 part{i+1}.gif...")
                        QtWidgets.QApplication.processEvents()
                        
                        # 檢查 write_gif 方法是否存在
                        if not hasattr(gif_segment, 'write_gif'):
                            print(f"錯誤：part{i+1} 物件沒有 write_gif 方法")
                            continue
                            continue
                        
                        # 使用更安全的 GIF 輸出參數
                        try:
                            gif_segment.write_gif(output_file, fps=fps_value, logger=None)
                        except Exception as gif_error:
                            print(f"GIF輸出失敗，嘗試備用方法：{str(gif_error)}")
                            # 嘗試使用預設參數
                            try:
                                gif_segment.write_gif(output_file, fps=fps_value)
                            except Exception as gif_error2:
                                print(f"part{i+1} GIF輸出完全失敗：{str(gif_error2)}")
                                continue
                        
                        # 驗證檔案是否成功建立
                        if os.path.exists(output_file):
                            file_size = os.path.getsize(output_file)
                            if file_size > 0:
                                print(f"Part{i+1} 完成 - 檔案大小: {file_size/1024:.1f}KB")
                            else:
                                print(f"警告：part{i+1} 檔案大小為0")
                                os.remove(output_file)  # 刪除空檔案
                        else:
                            print(f"警告：part{i+1} 檔案建立失敗")
                            
                    except Exception as e:
                        print(f"處理 part{i+1} 時發生錯誤：{str(e)}")
                        print(f"錯誤詳情：{traceback.format_exc()}")
                        continue
                        
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "影片處理錯誤", f"讀取或處理影片時發生錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
                return

            # 關閉影片檔案
            video.close()
            print("處理完成")

            # 更新進度到90%
            self.progressBar.setValue(90)
            self.label_progress.setText("正在調整檔案大小...")
            QtWidgets.QApplication.processEvents()

            max_size = 5 * 1024 * 1024  # 5MB in bytes

            # 檢查檔案大小如果過大進行縮小
            files_to_resize = []
            for i in range(1, 6):
                file_path = f"{output_name}_part{i}.gif"
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    if file_size > max_size:
                        files_to_resize.append((i, file_size))
                        print(f"檔案 part{i} 大小：{file_size/1024/1024:.2f}MB，需要調整")

            if files_to_resize:
                print("開始調整檔案大小...")
                for idx, (i, file_size) in enumerate(files_to_resize):
                    resize_progress = 90 + (idx * 2)  # 90-94%之間
                    self.progressBar.setValue(resize_progress)
                    self.label_progress.setText(f"正在調整 part{i} 檔案大小...")
                    QtWidgets.QApplication.processEvents()
                    
                    try:
                        im = Image.open(f"{output_name}_part{i}.gif")
                        # 計算縮放比例
                        original_width, original_height = im.size
                        scale_factor = (max_size / file_size) ** 0.5
                        new_width = int(original_width * scale_factor * 0.85)
                        new_height = int(original_height * scale_factor * 0.85)

                        resize_frames = [frame.resize((new_width, new_height)) for frame in ImageSequence.Iterator(im)]
                        resize_frames[0].save(f"{output_name}_part{i}.gif", save_all=True, append_images=resize_frames[1:])
                        print(f"Part{i} 調整完成!")
                        im.close()
                    except Exception as e:
                        print(f"調整 part{i} 時發生錯誤：{e}")
            else:
                print("所有檔案大小都符合要求")

            # 修改最後一個字節為21
            self.progressBar.setValue(95)
            self.label_progress.setText("正在修復GIF檔案...")
            QtWidgets.QApplication.processEvents()
            self.fix_gif_trailer()

            # 完成處理
            self.progressBar.setValue(100)
            self.label_progress.setText("處理完成！")
            QtWidgets.QApplication.processEvents()
            
            # 3秒後隱藏進度條
            QtCore.QTimer.singleShot(3000, lambda: (
                self.progressBar.setVisible(False),
                self.label_progress.setVisible(False)
            ))
            
            QtWidgets.QMessageBox.information(self, "完成", "影片切片處理完成！", QtWidgets.QMessageBox.Yes)
            
        except Exception as e:
            self.progressBar.setVisible(False)
            self.label_progress.setVisible(False)
            QtWidgets.QMessageBox.critical(self, "處理錯誤", f"處理影片時發生錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
            print(f"split_video_to_gifs error: {traceback.format_exc()}")
    
    def fix_gif_trailer(self):
        try:
            output_name = self.output_name.toPlainText().strip()
            if not output_name:
                QtWidgets.QMessageBox.warning(self, "錯誤", "請先設定輸出檔案名稱", QtWidgets.QMessageBox.Yes)
                return
                
            modified_files = []
            error_files = []
            
            for i in range(1, 6):
                path = f"{output_name}_part{i}.gif"
                try:
                    if not os.path.exists(path):
                        error_files.append(f"part{i} (檔案不存在)")
                        continue
                        
                    with open(path, 'rb') as f:
                        gif_data = bytearray(f.read())

                    # 修改最後一個字節為 21
                    if len(gif_data) >= 2:
                        gif_data[-1] = 0x21
                        modified_files.append(f"part{i}")
                    else:
                        error_files.append(f"part{i} (檔案太小)")
                        continue

                    # 保存修改後的 GIF 檔案
                    with open(path, 'wb') as f:
                        f.write(gif_data)
                        
                except Exception as e:
                    error_files.append(f"part{i} ({str(e)})")
                    
            # 顯示結果
            if modified_files:
                message = f"成功修改：{', '.join(modified_files)}"
                if error_files:
                    message += f"\n失敗：{', '.join(error_files)}"
                QtWidgets.QMessageBox.information(self, "修改完成", message, QtWidgets.QMessageBox.Yes)
            else:
                QtWidgets.QMessageBox.warning(self, "修改失敗", f"所有檔案都修改失敗：{', '.join(error_files)}", QtWidgets.QMessageBox.Yes)
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "修改錯誤", f"修改GIF檔案時發生錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
            print(f"fix_gif_trailer error: {traceback.format_exc()}")

    def upload_gif(self):
        try:
            # 檢查選中的部分
            selected_parts = self.get_selected_parts()
            if not selected_parts:
                QtWidgets.QMessageBox.warning(self, "錯誤", "請選擇要上傳的GIF檔案", QtWidgets.QMessageBox.Yes)
                return
                
            output_name = self.output_name.toPlainText().strip()
            if not output_name:
                QtWidgets.QMessageBox.warning(self, "錯誤", "請輸入輸出檔案名稱", QtWidgets.QMessageBox.Yes)
                return
                
            workshop_name = self.workshop_name.toPlainText().strip()
            if not workshop_name:
                QtWidgets.QMessageBox.warning(self, "錯誤", "請輸入工作坊名稱", QtWidgets.QMessageBox.Yes)
                return
            
            # 檢查檔案是否存在
            missing_files = []
            for part in selected_parts:
                file_path = os.path.abspath(f"{output_name}_part{part}.gif")
                if not os.path.exists(file_path):
                    missing_files.append(f"part{part}")
                    
            if missing_files:
                QtWidgets.QMessageBox.warning(self, "檔案錯誤", 
                    f"以下檔案不存在：{', '.join(missing_files)}\n請先處理影片", 
                    QtWidgets.QMessageBox.Yes)
                return

            #判斷使用哪個瀏覽器
            driver = None
            try:
                if self.comboBox.currentText() == 'Edge':
                    op = selenium.webdriver.edge.options.Options()
                    op.page_load_strategy = "eager"
                    op.add_argument('--disable-blink-features=AutomationControlled')
                    driver = webdriver.Edge(options=op)
                elif self.comboBox.currentText() == 'Chrome':
                    op = selenium.webdriver.chrome.options.Options()
                    op.page_load_strategy = "eager"
                    op.add_argument('--disable-blink-features=AutomationControlled')
                    driver = webdriver.Chrome(options=op)
                else:
                    QtWidgets.QMessageBox.warning(self, "錯誤", "請選擇瀏覽器", QtWidgets.QMessageBox.Yes)
                    return
            except WebDriverException as e:
                QtWidgets.QMessageBox.critical(self, "瀏覽器錯誤", 
                    f"無法啟動瀏覽器，請確認已安裝對應的WebDriver：\n{str(e)}", 
                    QtWidgets.QMessageBox.Yes)
                return

            try:
                # 訪問網頁
                driver.get("https://steamcommunity.com/sharedfiles/edititem/767/3/")

                # 等待網頁加載
                try:
                    WebDriverWait(driver, 15).until(
                        lambda driver: driver.find_element(By.XPATH,
                            '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[1]/input'
                        )
                    )
                except TimeoutException:
                    QtWidgets.QMessageBox.warning(self, "網路錯誤", "Steam頁面載入超時，請檢查網路連線", QtWidgets.QMessageBox.Yes)
                    return

                # 嘗試自動登入
                if os.path.exists("user.txt"):
                    try:
                        with open("user.txt", "r", encoding="utf-8") as file:
                            line1 = file.readline().strip()
                            line2 = file.readline().strip()
                            
                        if line1 and line2:
                            print("嘗試自動登入...")
                            username_input = driver.find_element(By.XPATH,
                                '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[1]/input')
                            username_input.clear()
                            username_input.send_keys(line1)
                            
                            password_input = driver.find_element(By.XPATH,
                                '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[2]/input')
                            password_input.clear()
                            password_input.send_keys(line2)
                            
                            driver.find_element(By.CLASS_NAME, "LBS7IDpob52Sb4ZoKobh0").click()
                            driver.find_element(By.CLASS_NAME, "DjSvCZoKKfoNSmarsEcTS").click()
                        else:
                            print("帳號資料檔案內容錯誤")
                    except Exception as e:
                        print(f"自動登入失敗：{e}")
                else:
                    print("請手動輸入帳號密碼")

                # 判斷是否成功登入
                login_timeout = 60  # 60秒超時
                login_start_time = time.time()
                while True:
                    if time.time() - login_start_time > login_timeout:
                        QtWidgets.QMessageBox.warning(self, "登入超時", "登入等待超時", QtWidgets.QMessageBox.Yes)
                        return
                        
                    if driver.current_url == "https://steamcommunity.com/sharedfiles/edititem/767/3/":
                        print("登入成功")
                        break
                    time.sleep(1)

                # 開始上傳選中的部分
                upload_success = []
                upload_failed = []
                
                for idx, part_num in enumerate(selected_parts):
                    try:
                        print(f"正在上傳 part{part_num} ({idx+1}/{len(selected_parts)})...")
                        
                        # 從第二次循環開始，每次都要開一次新的工作坊頁面
                        if idx > 0:
                            driver.get("https://steamcommunity.com/sharedfiles/edititem/767/3/")
                            WebDriverWait(driver, 15).until(
                                lambda driver: driver.find_element(By.CLASS_NAME, 'titleField')
                            )

                        # 輸入標題
                        title_input = driver.find_element(By.CLASS_NAME, 'titleField')
                        title_input.clear()
                        title_input.send_keys(f"{workshop_name}_{part_num}")

                        # 上傳gif檔案
                        file_path = os.path.abspath(f"{output_name}_part{part_num}.gif")
                        file_input = driver.find_element(By.ID, 'file')
                        file_input.send_keys(file_path)

                        # 點擊同意條款
                        agreement_checkbox = driver.find_element(By.ID, "agree_terms")
                        if not agreement_checkbox.is_selected():
                            agreement_checkbox.click()

                        # 執行JavaScript命令
                        driver.execute_script('''
                            $J('[name=consumer_app_id]').val(480);
                            $J('[name=file_type]').val(0);
                            $J('[name=visibility]').val(0);
                        ''')

                        # 點擊提交
                        submit_button = driver.find_element(By.XPATH, '//*[@id="SubmitItemForm"]/div[6]/a[2]')
                        submit_button.click()
                        
                        # 等待提交完成
                        time.sleep(3)
                        upload_success.append(f"part{part_num}")
                        
                    except Exception as e:
                        print(f"上傳 part{part_num} 失敗：{e}")
                        upload_failed.append(f"part{part_num}")

                # 顯示上傳結果
                if upload_success:
                    message = f"成功上傳：{', '.join(upload_success)}"
                    if upload_failed:
                        message += f"\n失敗：{', '.join(upload_failed)}"
                    QtWidgets.QMessageBox.information(self, "上傳完成", message, QtWidgets.QMessageBox.Yes)
                else:
                    QtWidgets.QMessageBox.warning(self, "上傳失敗", f"所有檔案都上傳失敗：{', '.join(upload_failed)}", QtWidgets.QMessageBox.Yes)

            finally:
                if driver:
                    driver.quit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "上傳錯誤", f"上傳過程中發生錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
            print(f"upload_gif error: {traceback.format_exc()}")
            if 'driver' in locals() and driver:
                driver.quit()

    def on_all_checkbox_clicked(self):
        """當選擇"全部"時，取消其他選項"""
        if self.checkBox_all.isChecked():
            self.checkBox_part1.setChecked(False)
            self.checkBox_part2.setChecked(False)
            self.checkBox_part3.setChecked(False)
            self.checkBox_part4.setChecked(False)
            self.checkBox_part5.setChecked(False)
    
    def on_part_checkbox_clicked(self):
        """當選中任何數字時，取消"全部"選項"""
        sender = self.sender()
        if sender.isChecked():
            self.checkBox_all.setChecked(False)
        
        # 檢查是否沒有任何選項被選中，如果是則選中"全部"
        if not any([self.checkBox_part1.isChecked(), self.checkBox_part2.isChecked(), 
                   self.checkBox_part3.isChecked(), self.checkBox_part4.isChecked(), 
                   self.checkBox_part5.isChecked()]):
            self.checkBox_all.setChecked(True)

    def get_selected_parts(self):
        """獲取被選中的部分"""
        selected_parts = []
        if self.checkBox_all.isChecked():
            return [1, 2, 3, 4, 5]
        else:
            if self.checkBox_part1.isChecked():
                selected_parts.append(1)
            if self.checkBox_part2.isChecked():
                selected_parts.append(2)
            if self.checkBox_part3.isChecked():
                selected_parts.append(3)
            if self.checkBox_part4.isChecked():
                selected_parts.append(4)
            if self.checkBox_part5.isChecked():
                selected_parts.append(5)
        return selected_parts

    def closeEvent(self, event):
        """程式關閉時清理工作"""
        try:
            # 停止計時器
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()
            
            # 釋放影片資源
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
            
            print("程式已安全關閉")
            event.accept()
        except Exception as e:
            print(f"關閉程式時發生錯誤：{e}")
            event.accept()

#output_gif_prefix = "output_gif"  # 輸出 GIF 檔案前綴
# split_video_to_gifs(input_video, output_gif_prefix)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.setWindowTitle('SteamVideoCut')

    # style_file = './style.qss'
    # style_sheet = QSSLoader.read_qss_file(style_file)
    # ui.setStyleSheet(style_sheet)

    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    #apply_stylesheet(app, theme='dark_teal.xml')

    ui.show()
    sys.exit(app.exec_())

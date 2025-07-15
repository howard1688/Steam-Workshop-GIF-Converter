from moviepy.video.io.VideoFileClip import VideoFileClip
import selenium.webdriver.edge.options
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import cv2
import os
import time
import traceback
import re
import datetime
from PIL import Image
from PIL import ImageSequence
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# 定義影片處理執行緒
class VideoProcessingThread(QThread):
    # 定義信號
    progress_updated = pyqtSignal(int, str)  # 進度值, 狀態文字
    processing_finished = pyqtSignal(bool, str)  # 是否成功, 訊息
    file_completed = pyqtSignal(int, str, int)  # part編號, 檔案名稱, 檔案大小
    output_message = pyqtSignal(str)  # 新增：輸出訊息信號
    
    def __init__(self, video_path, output_name, start_time, finish_time, fps_value):
        super().__init__()
        self.video_path = video_path
        self.output_name = output_name
        self.start_time = start_time
        self.finish_time = finish_time
        self.fps_value = fps_value
        self.is_cancelled = False
        
    def cancel(self):
        self.is_cancelled = True
        
    def run(self):
        try:
            # 檢查檔案大小，提前警告
            file_size_mb = os.path.getsize(self.video_path) / (1024 * 1024)
            
            # 顯示載入訊息
            self.progress_updated.emit(0, f"正在載入影片檔案 ({file_size_mb:.1f}MB)...")
            self.output_message.emit(f"[INFO] 開始處理影片: {self.video_path}")
            self.output_message.emit(f"[INFO] 檔案大小: {file_size_mb:.2f} MB")
            
            if self.is_cancelled:
                return
                
            # 載入影片
            try:
                self.output_message.emit(f"[INFO] 正在載入 MoviePy VideoFileClip...")
                video = VideoFileClip(self.video_path)
                self.progress_updated.emit(20, "影片載入完成")
                self.output_message.emit(f"[SUCCESS] 影片載入成功")
            except Exception as load_error:
                self.output_message.emit(f"[ERROR] 載入影片失敗: {str(load_error)}")
                self.processing_finished.emit(False, f"無法載入影片檔案：{str(load_error)}")
                return
            
            if self.is_cancelled:
                video.close()
                return
                
            # 驗證影片基本屬性
            try:
                duration = video.duration
                size = video.size
                fps = video.fps
                self.progress_updated.emit(30, f"影片資訊讀取完成 - {duration:.1f}秒, {size}")
                self.output_message.emit(f"[INFO] 影片時長: {duration:.2f} 秒")
                self.output_message.emit(f"[INFO] 影片尺寸: {size[0]}x{size[1]}")
                self.output_message.emit(f"[INFO] 影片幀率: {fps:.2f} fps")
            except Exception as attr_error:
                video.close()
                self.output_message.emit(f"[ERROR] 讀取影片屬性失敗: {str(attr_error)}")
                self.processing_finished.emit(False, f"影片檔案資訊讀取失敗：{str(attr_error)}")
                return
            
            # 檢查影片長度
            if video.duration < self.finish_time:
                video.close()
                self.output_message.emit(f"[ERROR] 結束時間({self.finish_time}s)超過影片長度({video.duration:.2f}s)")
                self.processing_finished.emit(False, f"結束時間超過影片長度！影片總長度：{int(video.duration)}秒")
                return
            
            if self.is_cancelled:
                video.close()
                return
                
            # 裁剪影片時間段
            self.progress_updated.emit(40, f"正在裁剪時間段: {self.start_time}-{self.finish_time}秒...")
            self.output_message.emit(f"[INFO] 裁剪時間段: {self.start_time}s - {self.finish_time}s")
            video = video.subclipped(self.start_time, self.finish_time)
            self.output_message.emit(f"[SUCCESS] 時間裁剪完成")
            
            if self.is_cancelled:
                video.close()
                return
                
            # 縮放影片尺寸大小
            self.progress_updated.emit(50, "正在調整影片尺寸...")
            self.output_message.emit(f"[INFO] 調整影片尺寸至 770x449...")
            video = video.resized((770,449))
            self.output_message.emit(f"[SUCCESS] 尺寸調整完成")
            
            if self.is_cancelled:
                video.close()
                return
                
            # 獲取影片寬高
            width, height = video.size
            
            # 計算每個片段寬度
            segment_width = (width - 20) / 5
            self.output_message.emit(f"[INFO] 每個片段寬度: {segment_width:.2f} 像素")
            
            # 驗證尺寸參數
            if segment_width <= 0:
                video.close()
                self.output_message.emit(f"[ERROR] 影片寬度太小，無法分割成5部分")
                self.processing_finished.emit(False, "影片寬度太小，無法分割成5部分")
                return
            
            # 開始生成GIF
            self.progress_updated.emit(60, "開始生成GIF檔案...")
            
            for i in range(5):
                if self.is_cancelled:
                    video.close()
                    return
                    
                # 更新進度條
                progress_value = 60 + (i * 6)
                self.progress_updated.emit(progress_value, f"正在處理 part{i+1} ({i+1}/5)...")
                
                # 計算每個 GIF 的起始和結束位置
                start_x = int(i * segment_width + i * 5)
                end_x = int(start_x + segment_width)
                
                # 確保座標在有效範圍內
                start_x = max(0, start_x)
                end_x = min(width, end_x)
                
                # 檢查裁剪區域是否有效
                if end_x <= start_x or end_x - start_x < 10:
                    continue
                
                # 裁剪影片
                try:
                    if start_x < 0 or end_x > width or start_x >= end_x:
                        continue
                        
                    # 執行裁剪操作
                    gif_segment = video.cropped(x1=start_x, x2=end_x, y1=0, y2=height)
                    
                    if gif_segment is None:
                        continue
                    
                    # 輸出 GIF 檔案
                    output_file = f"{self.output_name}_part{i + 1}.gif"
                    self.output_message.emit(f"[INFO] 開始生成 {output_file}...")
                    self.output_message.emit(f"[INFO] 裁剪區域: x={start_x}-{end_x}, y=0-{height}")
                    
                    # 更新進度到具體的GIF生成階段
                    gif_progress = 60 + (i * 6) + 3
                    self.progress_updated.emit(gif_progress, f"正在生成 part{i+1}.gif...")
                    
                    if not hasattr(gif_segment, 'write_gif'):
                        self.output_message.emit(f"[ERROR] gif_segment 沒有 write_gif 方法")
                        continue
                    
                    # 生成 GIF
                    try:
                        self.output_message.emit(f"[INFO] 使用 FPS: {self.fps_value}")
                        gif_segment.write_gif(output_file, fps=self.fps_value, logger=None)
                        self.output_message.emit(f"[SUCCESS] {output_file} 生成成功 (方法1)")
                    except Exception as e1:
                        try:
                            self.output_message.emit(f"[WARN] 方法1失敗，嘗試方法2: {str(e1)}")
                            gif_segment.write_gif(output_file, fps=self.fps_value)
                            self.output_message.emit(f"[SUCCESS] {output_file} 生成成功 (方法2)")
                        except Exception as e2:
                            self.output_message.emit(f"[ERROR] 生成 {output_file} 失敗: {str(e2)}")
                            continue
                    
                    # 驗證檔案是否成功建立
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        if file_size > 0:
                            self.output_message.emit(f"[SUCCESS] {output_file} 檔案大小: {file_size/1024:.2f} KB")
                            self.file_completed.emit(i+1, output_file, file_size)
                        else:
                            self.output_message.emit(f"[ERROR] {output_file} 檔案大小為 0，刪除檔案")
                            os.remove(output_file)
                        
                except Exception as e:
                    error_msg = f"處理 part{i+1} 時發生錯誤：{str(e)}"
                    self.output_message.emit(f"[ERROR] {error_msg}")
                    print(error_msg)
                    continue
            
            # 關閉影片檔案
            video.close()
            
            if self.is_cancelled:
                return
                
            # 處理檔案大小調整
            self.progress_updated.emit(90, "正在調整檔案大小...")
            self._resize_large_files()
            
            if self.is_cancelled:
                return
                
            # 修復GIF檔案
            self.progress_updated.emit(95, "正在修復GIF檔案...")
            self._fix_gif_trailer()
            
            # 完成處理
            self.progress_updated.emit(100, "處理完成！")
            self.processing_finished.emit(True, "影片切片處理完成！")
            
        except Exception as e:
            self.processing_finished.emit(False, f"處理影片時發生錯誤：{str(e)}")
    
    def _resize_large_files(self):
        """調整過大的檔案"""
        max_size = 5 * 1024 * 1024  # 5MB
        
        for i in range(1, 6):
            if self.is_cancelled:
                return
                
            file_path = f"{self.output_name}_part{i}.gif"
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > max_size:
                    try:
                        im = Image.open(file_path)
                        original_width, original_height = im.size
                        scale_factor = (max_size / file_size) ** 0.5
                        new_width = int(original_width * scale_factor * 0.85)
                        new_height = int(original_height * scale_factor * 0.85)

                        resize_frames = [frame.resize((new_width, new_height)) for frame in ImageSequence.Iterator(im)]
                        resize_frames[0].save(file_path, save_all=True, append_images=resize_frames[1:])
                        im.close()
                    except Exception:
                        pass
    
    def _fix_gif_trailer(self):
        """修復GIF檔案結尾"""
        for i in range(1, 6):
            if self.is_cancelled:
                return
                
            path = f"{self.output_name}_part{i}.gif"
            try:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        gif_data = bytearray(f.read())
                    
                    if len(gif_data) >= 2:
                        gif_data[-1] = 0x21
                        
                        with open(path, 'wb') as f:
                            f.write(gif_data)
            except Exception:
                pass

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
        
        # 執行緒相關
        self.processing_thread = None
        self.is_processing = False

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
        
        # 調整主視窗大小以容納新增元素（移除label_progress後調整）
        MainWindow.resize(505, 695)
        MainWindow.setMinimumSize(QtCore.QSize(505, 695))
        MainWindow.setMaximumSize(QtCore.QSize(505, 695))
        
        # 新增進度條
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 510, 481, 25))
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(True)  # 初始顯示
        self.progressBar.setValue(0)  # 初始值為0
        self.progressBar.setMaximum(100)  # 設定最大值
        self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")  # 設定初始訊息
        
        # 移除進度標籤（不再需要）
        # self.label_progress = QtWidgets.QLabel(self.centralwidget)
        # self.label_progress.setGeometry(QtCore.QRect(10, 540, 481, 20))
        # self.label_progress.setObjectName("label_progress")
        # self.label_progress.setText("等待開始...")
        # self.label_progress.setAlignment(QtCore.Qt.AlignCenter)
        # self.label_progress.setVisible(True)  # 初始顯示
        
        # 新增 CMD 輸出顯示區域
        self.textEdit_output = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_output.setGeometry(QtCore.QRect(10, 545, 401, 120))  # 向上移動25像素
        self.textEdit_output.setObjectName("textEdit_output")
        self.textEdit_output.setVisible(False)  # 初始隱藏
        self.textEdit_output.setReadOnly(True)  # 設為唯讀
        font = QtGui.QFont("Consolas", 9)  # 使用等寬字體便於顯示 cmd 輸出
        self.textEdit_output.setFont(font)
        self.textEdit_output.setPlaceholderText("處理輸出將顯示在這裡...")
        
        # 設置文字編輯器樣式
        self.textEdit_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        # 新增清空輸出按鈕
        self.pushButton_clear_output = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_clear_output.setGeometry(QtCore.QRect(420, 545, 71, 30))  # 向上移動25像素
        self.pushButton_clear_output.setObjectName("pushButton_clear_output")
        self.pushButton_clear_output.setText("清空輸出")
        self.pushButton_clear_output.setVisible(False)  # 初始隱藏
        self.pushButton_clear_output.clicked.connect(self.clear_output)
        
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
        MainWindow.setWindowTitle(_translate("MainWindow", "Steam Workshop GIF Converter"))
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
        print("初始化按鈕連接...")  # 除錯訊息
        self.pushButton.clicked.connect(self.toggle_processing)  # 連接切片/取消函數
        self.time_start.textChanged.connect(self.read_time_start)
        self.time_start_2.textChanged.connect(self.read_time_start)
        self.time_finish.textChanged.connect(self.read_time_finish)
        self.time_finish_2.textChanged.connect(self.read_time_finish)
        self.toolButtonInput.clicked.connect(self.InpurDir)           # 連接影片路徑選擇函數
        self.pushButton_3.clicked.connect(self.upload_gif)
        # self.toolButtonOutput.clicked.connect(self.SaveResults)
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton_fixgif.clicked.connect(self.fix_gif_trailer)
        print("按鈕連接完成！")  # 除錯訊息
        
        # 設置 label 顯示五個方框的預覽圖
        self.setup_preview_boxes()
            
        self.output_name.setPlainText("output_gif")
        self.workshop_name.setPlainText('gif') # 設置上傳名稱
        
        # 移除啟動歡迎訊息，改為在進度條顯示
        # self.show_startup_message()

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
        print("InpurDir 方法被調用了！")  # 除錯訊息
        try:
            # 更新進度條為載入狀態
            self.progressBar.setValue(10)
            self.progressBar.setFormat("正在選擇影片檔案...")
            QtWidgets.QApplication.processEvents()
            
            video_type = [".mp4", ".mkv", ".MOV", ".avi", ".m4v"]
            file_dialog = QtWidgets.QFileDialog.getOpenFileName(
                self, 
                "選擇影片檔案", 
                "", 
                "影片檔案 (*.mp4 *.mkv *.MOV *.avi *.m4v);;所有檔案(*.*)"
            )
            self.video_path = file_dialog[0]
            print(f"選擇的檔案路徑：{self.video_path}")  # 除錯訊息

            # 檢查是否選擇了檔案
            if not self.video_path:
                self.progressBar.setValue(0)
                self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")
                return

            # 檢查檔案是否存在
            self.progressBar.setValue(20)
            self.progressBar.setFormat("📁 驗證檔案...")
            QtWidgets.QApplication.processEvents()
            
            if not os.path.exists(self.video_path):
                QtWidgets.QMessageBox.warning(self, "錯誤", "檔案不存在", QtWidgets.QMessageBox.Yes)
                self.progressBar.setValue(0)
                self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")
                return

            # 檢查檔案大小
            file_size = os.path.getsize(self.video_path)
            if file_size == 0:
                QtWidgets.QMessageBox.warning(self, "錯誤", "檔案內容為空檔案", QtWidgets.QMessageBox.Yes)
                self.progressBar.setValue(0)
                self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")
                return

            # 判斷是否為支援的影片格式
            self.progressBar.setValue(30)
            self.progressBar.setFormat("🔍 檢查檔案格式...")
            QtWidgets.QApplication.processEvents()
            
            is_supported = False
            for vdi in video_type:
                if vdi.lower() in self.video_path.lower():
                    is_supported = True
                    break
            
            if not is_supported:
                QtWidgets.QMessageBox.warning(self, "格式錯誤", 
                    f"不支援該格式！\n支援格式：{', '.join(video_type)}", 
                    QtWidgets.QMessageBox.Yes)
                self.progressBar.setValue(0)
                self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")
                return

            print("選擇輸入影片路徑", self.video_path)
            self.textEdit.setPlainText(self.video_path)
            print("videoIsOpen")

            # 計算影片長度,並設置滑動軸中時間
            self.progressBar.setValue(50)
            self.progressBar.setFormat("📊 分析影片資訊...")
            QtWidgets.QApplication.processEvents()
            
            try:
                duration = self.get_video_duration()
                if duration <= 0:
                    QtWidgets.QMessageBox.warning(self, "錯誤", "無法讀取影片時長，請檢查影片檔案", QtWidgets.QMessageBox.Yes)
                    self.progressBar.setValue(0)
                    self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")
                    return
                    
                self.progressBar.setValue(70)
                self.progressBar.setFormat("⚙️ 設定時間參數...")
                QtWidgets.QApplication.processEvents()
                
                self.time_start.setPlainText("00")
                self.time_start_2.setPlainText("00")
                if duration < 15:
                    self.finish_time = duration
                    self.time_finish.setPlainText("00")
                    self.time_finish_2.setPlainText(str(duration))
                else:
                    self.finish_time = 10
                    self.time_finish.setPlainText("00")
                    self.time_finish_2.setPlainText("10")

                # 嘗試開啟影片預覽
                self.progressBar.setValue(90)
                self.progressBar.setFormat("🎬 初始化影片預覽...")
                QtWidgets.QApplication.processEvents()
                
                if self.cap.isOpened():
                    self.cap.release()
                
                self.cap.open(self.video_path)
                if not self.cap.isOpened():
                    QtWidgets.QMessageBox.warning(self, "警告", "無法開啟影片預覽，但可以繼續處理", QtWidgets.QMessageBox.Yes)
                else:
                    self.timer.start(30)   # 設置影片播放計時器
                
                # 載入完成
                self.progressBar.setValue(100)
                self.progressBar.setFormat(f"✅ 影片載入完成！({duration:.1f}秒) - 可開始製作GIF")
                
                # 移除CMD輸出訊息，狀態直接顯示在進度條上
                                    
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "錯誤", f"讀取影片時發生錯誤：{str(e)}", QtWidgets.QMessageBox.Yes)
                self.progressBar.setValue(0)
                self.progressBar.setFormat("🚀 Steam Workshop GIF Converter  - 請選擇影片檔案開始")
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
            
            # 在影片上繪製分割線
            pixmap = self.draw_division_lines(pixmap)
            
            self.label.setScaledContents(True)
            # 影片流置於label中間播放
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setPixmap(pixmap)

    def draw_division_lines(self, pixmap):
        """在影片幀上繪製黑色分割線"""
        # 複製 pixmap 以免修改原始數據
        pixmap_with_lines = pixmap.copy()
        
        # 獲取影片預覽區域的尺寸
        width = pixmap_with_lines.width()
        height = pixmap_with_lines.height()
        
        # 根據影片寬度動態計算線條粗細（調整為更細的線條）
        line_width = max(3, int(width * 0.006))  # 最少1像素，更細的線條

        painter = QPainter(pixmap_with_lines)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 設置動態粗細的黑色畫筆
        pen = QPen(Qt.black, line_width, Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)  # 設置圓形線條端點
        painter.setPen(pen)
        
        # 計算分割線的位置（將寬度分成5等份）
        segment_width = width / 5
        
        # 繪製4條分割線（分成5部分需要4條線）
        for i in range(1, 5):
            x = int(i * segment_width)
            painter.drawLine(x, 0, x, height)
        
        painter.end()
        
        return pixmap_with_lines

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
        """舊版本相容性 - 重導向到新的執行緒版本"""
        self.toggle_processing()
    
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
            # 取消正在進行的處理
            if self.is_processing and self.processing_thread:
                self.processing_thread.cancel()
                self.processing_thread.wait(3000)  # 等待最多3秒
                if self.processing_thread.isRunning():
                    self.processing_thread.terminate()
                    
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

    def toggle_processing(self):
        """切換處理狀態（開始/取消）"""
        print("toggle_processing 方法被調用了！")  # 除錯訊息
        if not self.is_processing:
            print("開始處理...")  # 除錯訊息
            self.start_processing()
        else:
            print("取消處理...")  # 除錯訊息
            self.cancel_processing()
    
    def start_processing(self):
        """開始影片處理"""
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
        
        # 計算時間
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

        # 檢查檔案大小，提前警告
        file_size_mb = os.path.getsize(self.video_path) / (1024 * 1024)
        
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

        # 設定處理狀態
        self.is_processing = True
        self.pushButton.setText("取消")
        self.pushButton.setStyleSheet("background-color: #ff6b6b; color: white;")
        
        # 設定進度條和輸出區域
        self.progressBar.setFormat("🚀 開始處理...")
        self.textEdit_output.setVisible(True)  # 顯示輸出區域
        self.pushButton_clear_output.setVisible(True)  # 顯示清空按鈕
        self.progressBar.setValue(0)
        
        # 清空輸出區域
        self.textEdit_output.clear()
        self.textEdit_output.append("[START] 開始影片處理...")
        
        # 禁用其他控制項
        self.toolButtonInput.setEnabled(False)
        self.pushButton_fixgif.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        
        # 建立並啟動處理執行緒
        self.processing_thread = VideoProcessingThread(
            self.video_path, output_name, self.start_time, self.finish_time, fps_value
        )
        
        # 連接信號
        self.processing_thread.progress_updated.connect(self.on_progress_updated)
        self.processing_thread.processing_finished.connect(self.on_processing_finished)
        self.processing_thread.file_completed.connect(self.on_file_completed)
        self.processing_thread.output_message.connect(self.on_output_message)  # 連接新的輸出信號
        
        # 啟動執行緒
        self.processing_thread.start()
    
    def cancel_processing(self):
        """取消影片處理"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.cancel()
            self.processing_thread.wait(5000)  # 等待最多5秒
            
            if self.processing_thread.isRunning():
                self.processing_thread.terminate()
                self.processing_thread.wait()
        
        self.on_processing_finished(False, "處理已取消")
    
    def on_progress_updated(self, value, message):
        """更新進度條"""
        self.progressBar.setValue(value)
        self.progressBar.setFormat(message)
    
    def on_output_message(self, message):
        """處理輸出訊息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.textEdit_output.append(formatted_message)
        
        # 自動捲動到最新訊息
        cursor = self.textEdit_output.textCursor()
        cursor.movePosition(cursor.End)
        self.textEdit_output.setTextCursor(cursor)
        
        # 強制更新UI
        QtWidgets.QApplication.processEvents()
    
    def on_file_completed(self, part_num, filename, file_size):
        """檔案完成處理"""
        message = f"Part{part_num} 完成 - 檔案大小: {file_size/1024:.1f}KB"
        print(message)
        self.on_output_message(f"[COMPLETE] {message}")
    
    def on_processing_finished(self, success, message):
        """處理完成"""
        # 恢復UI狀態
        self.is_processing = False
        self.pushButton.setText("切片")
        self.pushButton.setStyleSheet("")  # 恢復原始樣式
        
        # 重新啟用控制項
        self.toolButtonInput.setEnabled(True)
        self.pushButton_fixgif.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        
        if success:
            self.on_output_message(f"[FINISH] 處理成功完成！")
            self.on_output_message(f"[RESULT] {message}")
            # 設定完成狀態，但保持進度條和標籤顯示
            self.progressBar.setValue(100)  # 確保進度條顯示100%
            self.progressBar.setFormat("🎉 處理完成！")
            QtWidgets.QMessageBox.information(self, "完成", message, QtWidgets.QMessageBox.Yes)
        else:
            self.on_output_message(f"[ERROR] 處理失敗: {message}")
            # 即使失敗也保持進度條顯示，但重置為0
            self.progressBar.setValue(0)
            self.progressBar.setFormat("❌ 處理失敗 - 請重新開始")
            if "取消" not in message:
                QtWidgets.QMessageBox.critical(self, "處理錯誤", message, QtWidgets.QMessageBox.Yes)
        
        # 清理執行緒
        if self.processing_thread:
            self.processing_thread = None

    def clear_output(self):
        """清空輸出區域"""
        self.textEdit_output.clear()
        self.textEdit_output.append("[CLEARED] 輸出已清空")

    def setup_preview_boxes(self):
        """初始化 - 不顯示預設圖片"""
        # 不顯示任何預設圖片，等待影片載入
        pass

    def show_startup_message(self):
        """顯示程式啟動歡迎訊息 - 已移除，狀態訊息現在顯示在進度條上"""
        pass


if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')  # 設置現代化的視覺風格
        
        # 設置應用程式圖示（如果有的話）
        # app.setWindowIcon(QtGui.QIcon('icon.ico'))
        
        # 創建主視窗
        MainWindow = Ui_MainWindow()
        MainWindow.show()
        
        print("Steam Workshop GIF Converter 程式已啟動")
        
        # 啟動應用程式事件循環
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程式啟動失敗: {e}")
        print(f"錯誤詳情: {traceback.format_exc()}")
        input("按 Enter 鍵退出...")

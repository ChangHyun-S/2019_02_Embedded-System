# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coap_client.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

'''
Coap_client.py
20155136 심창현
'''

import time
from PyQt5 import QtCore, QtGui, QtWidgets
from coapthon.client.helperclient import HelperClient

# IP, Port, Path 설정
Ip = '192.168.0.76'
Port = 5683
Path = 'observe'

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(620, 320)
        
        # Coap 설정
        self.coap_setup(host = Ip, port= Port)
        
        # 배경 색 지정 (white)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)
        
        # 윈도우 설정
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # 버튼 설정
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 481, 281))
        self.textBrowser.setObjectName("textBrowser")
        self.btn_Observe = QtWidgets.QPushButton(self.centralwidget)
        self.btn_Observe.setGeometry(QtCore.QRect(500, 120, 111, 51))
        self.btn_Observe.setObjectName("btn_Observe")
        self.btn_Get = QtWidgets.QPushButton(self.centralwidget)
        self.btn_Get.setGeometry(QtCore.QRect(500, 180, 111, 51))
        self.btn_Get.setObjectName("btn_Get")
        self.btn_Test = QtWidgets.QPushButton(self.centralwidget)
        self.btn_Test.setGeometry(QtCore.QRect(500, 240, 111, 51))
        self.btn_Test.setObjectName("btn_Test")
        
        # 버튼 함수지정
        self.btn_Observe.clicked.connect(self.coap_observe)
        self.btn_Get.clicked.connect(self.coap_get)
        self.btn_Test.clicked.connect(self.connection_test)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CoAP Client 20155136 심창현"))
        self.btn_Observe.setText(_translate("MainWindow", "Observe"))
        self.btn_Get.setText(_translate("MainWindow", "현재 상태"))
        self.btn_Test.setText(_translate("MainWindow", "통신 테스트"))
        
    # Coap 설정
    def coap_setup(self, host, port):
        self.client = HelperClient(server=(host, port)) # 클래스 변수로 Client 객체 저장
    
    # observe 실행 시 callback 함수
    def OnReceiptionOfOserve(self, response):
        # observe 받을 시 현재 시간과 payload를 textBrowser에 추가
        self.textBrowser.append('observe\t' + time.strftime('%p %I:%M:%S ') + response.payload)
        
    # 현재 상태 버튼을 누르면 실행
    def coap_get(self):
        # GET 전송
        response = self.client.get(path=Path, timeout=3)
        # GET 받을 시 현재 시간과 payload를 textBrowser에 추가
        self.textBrowser.append('get\t' + time.strftime('%p %I:%M:%S ') + response.payload)  # Text board에 수신한 response 출력    

    # Observe 버튼을 누르면 실행
    def coap_observe(self):
        # Observe가 실행중일동안 GET과 통신 테스트를 하면 클라이언트 종료됨.
        # 따라서 observe 버튼을 누르면 현재 상태 버튼과 observe 버튼을 비활성화 시킴
        self.btn_Get.setEnabled(False)
        self.btn_Test.setEnabled(False)
        # 서버에 observe 요청
        observe = self.client.observe(path=Path, callback=self.OnReceiptionOfOserve)
        
    # 통신 테스트 버튼 누르면 실행
    def connection_test(self):
        # path 없이 서버 리소스 지정
        res = self.client.get(path='', timeout=3)
        
        # 응답이 없으면 실패, 아니면 성공
        if res == None:
            self.textBrowser.append('통신 테스트\t' + time.strftime('%p %I:%M:%S ') + "실패")
        else:
            self.textBrowser.append('통신 테스트\t' + time.strftime('%p %I:%M:%S ') + "성공")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

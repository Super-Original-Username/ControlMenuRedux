# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'trckGUI.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(702, 466)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tableWidget = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cdBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.cdBtn.setObjectName("cdBtn")
        self.verticalLayout.addWidget(self.cdBtn)
        self.openBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.openBtn.setObjectName("openBtn")
        self.verticalLayout.addWidget(self.openBtn)
        self.closeBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.closeBtn.setObjectName("closeBtn")
        self.verticalLayout.addWidget(self.closeBtn)
        self.idleBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.idleBtn.setObjectName("idleBtn")
        self.verticalLayout.addWidget(self.idleBtn)
        self.IMEIBox = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IMEIBox.sizePolicy().hasHeightForWidth())
        self.IMEIBox.setSizePolicy(sizePolicy)
        self.IMEIBox.setObjectName("IMEIBox")
        self.verticalLayout.addWidget(self.IMEIBox)
        self.trackBtn = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.trackBtn.sizePolicy().hasHeightForWidth())
        self.trackBtn.setSizePolicy(sizePolicy)
        self.trackBtn.setObjectName("trackBtn")
        self.verticalLayout.addWidget(self.trackBtn)
        self.stopBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.stopBtn.setObjectName("stopBtn")
        self.verticalLayout.addWidget(self.stopBtn)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Latitude"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Longitude"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Altitude"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Time"))
        self.cdBtn.setText(_translate("MainWindow", "Attempt cutdown"))
        self.openBtn.setText(_translate("MainWindow", "Open valve"))
        self.closeBtn.setText(_translate("MainWindow", "Close valve"))
        self.idleBtn.setText(_translate("MainWindow", "Send idle command"))
        self.IMEIBox.setPlaceholderText(_translate("MainWindow", "Iridium IMEI"))
        self.trackBtn.setText(_translate("MainWindow", "Start tracking"))
        self.stopBtn.setText(_translate("MainWindow", "Stop tracking"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


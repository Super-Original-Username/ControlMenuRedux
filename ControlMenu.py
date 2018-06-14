# Imports
import sys
import os
import datetime

# PyQt imports
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import MySQLdb

from trckGUI import Ui_MainWindow


class Updater(QObject):
    def __init__(self, lat, lon, alt, time, seconds):
        super(Updater, self).__init__()
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.time = time
        self.seconds = seconds

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def get_alt(self):
        return self.alt

    def get_time(self):
        return self.time

    def get_seconds(self):
        return self.seconds


class Unbuffered:
    """This gets rid of the serial buffer"""

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush

    def flush(self):
        self.stream.flush

    def close(self):
        self.stream.close


class Iridium(QThread):
    new_coords = pyqtSignal(list)
    no_iridium = pyqtSignal()

    def __init__(self, host, user, passwd, name, IMEI):
        super(Iridium, self).__init__()
        # self.moveToThread(self.main_window.iridium_thread)
        self.iridium_interrupt = False
        self.main_window = MainWindow
        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name
        self.IMEI = IMEI

    def __del__(self):
        self.wait()

    def run(self):
        self.new_loc = ''
        prev = ''
        connected = False
        attempts = 0
        while not connected and not self.iridium_interrupt:
            if attempts < 20:
                try:
                    db = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name)
                    cmd = 'select gps_lat, gps_long, gps_alt, gps_time from gps where gps_IMEI = %s order by pri_key DESC LIMIT 1' % self.IMEI
                    db.query(cmd)
                    connected = True

                    if self.iridium_interrupt:
                        db.close()
                        connected = False
                except:
                    print("Failed ot connect, trying again in 1 second")
                    attempts += 1
                    self.sleep(1)
            else:
                print("Too many attempts, quitting")
                self.interrupt()
                self.main_window.no_iridium.emit()
            while connected:
                try:
                    self.new_loc = ''
                    r = db.store_result()
                    result = r.fetch_row()[0]
                    if result is not prev:
                        prev = result
                        print(result)
                        time = result[3].split(':')
                        hours = int(time[0])
                        minutes = int(time[1])
                        seconds = int(time[2])
                        seconds = seconds + (hours * 3600) + (minutes * 60)
                        lat = float(result[0])
                        lon = float(result[1])
                        alt = float(result[2])

                        try:
                            self.new_loc = [lat, lon, alt, str(time), seconds]
                            print(self.new_loc)
                        except:
                            print("Location data could not be updated")

                        try:
                            try:
                                if self.new_loc is not '':
                                    self.new_coords.emit(self.new_loc)
                            except Exception as e:
                                print(e)
                        except Exception as e:
                            print(e)
                except:
                    print("ERROR: could not find any data. Please check the IMEI for your modem")
                self.sleep(2)
        try:
            db.close()
        except Exception as e:
            print(e)
        pass

    def interrupt(self):
        self.iridium_interrupt = True


class Emailer(QThread):
    def __init__(self):
        super(Emailer, self).__init__()


class MainWindow(Ui_MainWindow):

    def __init__(self, dialog):
        super(MainWindow, self).__init__()

        self.setupUi(dialog)

        self.db_host = 'eclipse.rci.montana.edu'
        self.db_user = 'antenna'
        self.db_passwd = 'tracker'
        self.db_name = 'freemanproject'

        self.cmd_emailer = Emailer()
        self.cmd_thread = QThread()
        self.cmd_emailer.moveToThread(self.cmd_thread)
        self.iridium_thread = QThread()
        self.iridium_tracker = ''

        self.cmd_thread.start()

        self.cdBtn.clicked.connect(self.attempt_cutdown)
        self.cdBtn.setEnabled(False)
        self.openBtn.clicked.connect(self.open_valve)
        self.openBtn.setEnabled(False)
        self.closeBtn.clicked.connect(self.close_valve)
        self.closeBtn.setEnabled(False)
        self.idleBtn.clicked.connect(self.send_idle)
        self.idleBtn.setEnabled(False)
        self.trackBtn.clicked.connect(self.start_tracking)

        self.IMEI = ''
        self.email = ''
        self.e_pass = ''

        self.current = Updater(0, 0, 0, '', 0)

    def close_valve(self):
        print("closing valve")

    def attempt_cutdown(self):
        print("attempting cutdown")

    def open_valve(self):
        print("opening valve")

    def send_idle(self):
        print("sending idle command")

    def start_tracking(self):
        self.trackBtn.setEnabled(False)
        self.openBtn.setEnabled(True)
        self.closeBtn.setEnabled(True)
        self.cdBtn.setEnabled(True)
        self.idleBtn.setEnabled(True)
        self.IMEI = self.IMEIBox.text()
        self.iridium_tracker = Iridium(self.db_host, self.db_user, self.db_passwd, self.db_name, self.IMEI)
        self.iridium_tracker.moveToThread(self.iridium_thread)
        self.iridium_thread.started.connect(self.iridium_tracker.run)
        self.iridium_tracker.new_coords.connect(self.update_table)
        self.iridium_thread.start()

    def update_table(self, coords):
        new_data = Updater(coords[0], coords[1], coords[2], coords[3], coords[4])
        if new_data.get_lat() == 0.0 or new_data.get_lon() == 0.0 or new_data.get_alt() == 0.0:
            return

        if new_data.get_seconds() < self.current.get_seconds():
            return

        for item in coords:
            print(item)

        try:
            current_rows = self.tableWidget.rowCount()
            self.tableWidget.insertRow(current_rows)
            self.tableWidget.setItem(current_rows, 0, coords[0])
            self.tableWidget.setItem(current_rows, 1, coords[1])
            self.tableWidget.setItem(current_rows, 2, coords[2])
            self.tableWidget.setItem(current_rows, 3, coords[3])
        except:
            print("ERROR: The location data could not be updated")

        self.current = new_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = QMainWindow()
    m_gui = MainWindow(form)
    form.show()
    sys.stdout = Unbuffered(sys.stdout)

    sys._excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook
    app.exec_()

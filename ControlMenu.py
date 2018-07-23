''' Imports '''
import sys
import os
import time

''' PyQt imports '''
from email.mime.application import MIMEApplication

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import MySQLdb

''' Email imports '''
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

from trckGUI import Ui_MainWindow


''' This function sends command emails to the provided Iridium IMEI '''
class Emailer(QThread):

    def __init__(self, cmd, IMEI):
        super(Emailer, self).__init__()
        self.from_addr = 'msgc.borealis@gmail.com'
        self.to_addr = 'data@sbd.iridium.com'
        self.passwd = 'FlyHighN0w'
        self.cmd = cmd
        self.IMEI = IMEI

    # Closes the thread

    def __del__(self):
        self.quit()
        self.wait()

    # Reads in the command sent from the mainwindow thread. Filenames indicate the function that
    # the arduino should call when the pinstate (last 3 digits in the filename) is read in from the iridium

    def run(self):
        if self.cmd == 'cutdown':
            cmd_file = 'commands/cutdown_100.sbd'
        elif self.cmd == 'open':
            cmd_file = 'commands/open_010.sbd'
        elif self.cmd == 'close':
            cmd_file = 'commands/close_001.sbd'
        elif self.cmd == 'idle':
            cmd_file = 'commands/idle_000.sbd'

        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr
        msg['Subject'] = self.IMEI

        ''' Attaches the command file to an email '''
        with open(cmd_file, "rb") as command:
            msg.attach(MIMEApplication(command.read(),
                                       Content_Disposition='attachment; filename=%s' % os.path.basename(
                                           cmd_file),
                                       Name=os.path.basename(cmd_file)
                                       ))

        ''' Server login procedure, ends with sending the email to the Iridium address '''
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("msgc.borealis", "FlyHighN0w")
        text = msg.as_string()
        server.sendmail(self.from_addr, self.to_addr, text)
        if self.cmd == 'cutdown':
            print(self.cmd)

        self.__del__()


''' This really doesn't need to be here, but it makes tracking ever so slightly easier '''
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


''' This class eliminates any buffering from any stream used as this function's argument '''
class Unbuffered:

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush

    def flush(self):
        self.stream.flush

    def close(self):
        self.stream.close


''' This class handles all tracking for the Iridium modem '''
class Iridium(QThread):
    # Signal declarations for sending data between the tracking thread and the mainwindow thread
    new_coords = pyqtSignal(list)
    idle_send = pyqtSignal()
    no_iridium = pyqtSignal()

    def __init__(self, host, user, passwd, name, IMEI):
        super(Iridium, self).__init__()
        self.c = ''
        self.db = ''
        self.cmd = ''
        self.iridium_interrupt = False
        self.main_window = MainWindow
        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name
        self.IMEI = IMEI

    # Kills the thread and sends the idle command to the modem, to reset the pinstate back to 000
    def __del__(self):
        print("Killing tracker")
        self.idle_send.emit()
        self.quit()
        self.wait()

    # Pulls data from a MySQL database currently being hosted by Montana State University,
    # then sends it back to be logged by the mainwindow thread
    def run(self):
        self.new_loc = ''
        prev = ''
        connected = False
        attempts = 0
        while not connected and not self.iridium_interrupt:
            if attempts < 20:

                # Database login
                try:
                    self.db = MySQLdb.connect(
                        host=self.host, user=self.user, passwd=self.passwd, db=self.name)
                    self.db.autocommit(True)
                    self.cmd = 'select gps_lat, gps_long, gps_alt, gps_time from gps where gps_IMEI = %s order by pri_key DESC LIMIT 1' % self.IMEI
                    self.c = self.db.cursor()
                    connected = True

                    if self.iridium_interrupt:
                        self.db.close()
                        self.c.close()
                        connected = False
                except:
                    print("Failed to connect, trying again in 1 second")
                    attempts += 1
                    self.sleep(1)
            else:
                print("Too many attempts, quitting")
                self.interrupt()
                self.main_window.no_iridium.emit()
            while connected and not self.iridium_interrupt:

                # This loop fetches data from our server, then sends it to be logged if it is different from the
                # previously retreived data
                try:
                    self.new_loc = ''
                    try:
                        self.c.execute(self.cmd)
                        result = self.c.fetchone()
                    except Exception as e:
                        print(e)
                    if result != prev:
                        prev = result

                        # This converts the time pulled from the server to something a bit more legible
                        real_time = str(result[3])
                        time = result[3].split(':')
                        hours = int(time[0])
                        minutes = int(time[1])
                        seconds = int(time[2])
                        seconds = seconds + (hours * 3600) + (minutes * 60)
                        lat = float(result[0])
                        lon = float(result[1])
                        alt = float(result[2])

                        try:
                            self.new_loc = [lat, lon, alt, real_time, seconds]
                            # print(self.new_loc)
                        except:
                            print("Location data could not be updated")

                        try:
                            if self.new_loc is not '':
                                self.new_coords.emit(self.new_loc)
                        except Exception as e:
                            print(e)
                    '''else:
                        raise Exception(
                            "ERROR: data is same as last fetch or IMEI is incorrect")'''
                except Exception as e:
                    print(e)
                '''if not self.iridium_interrupt:
                    self.sleep(5)'''
        try:
            self.c.close()
            self.db.close()
            self.connected = False
        except Exception as e:
            print(e)
        pass

    def interrupt(self):
        self.iridium_interrupt = True


class MainWindow(Ui_MainWindow):

    def __init__(self, dialog):
        super(MainWindow, self).__init__()

        self.setupUi(dialog)

        self.db_host = 'eclipse.rci.montana.edu'
        self.db_user = 'antenna'
        self.db_passwd = 'tracker'
        self.db_name = 'freemanproject'

        # self.cmd_thread.start()

        self.cdBtn.clicked.connect(self.attempt_cutdown)
        self.cdBtn.setEnabled(False)
        self.openBtn.clicked.connect(self.open_valve)
        self.openBtn.setEnabled(False)
        self.closeBtn.clicked.connect(self.close_valve)
        self.closeBtn.setEnabled(False)
        self.idleBtn.clicked.connect(self.send_idle)
        self.idleBtn.setEnabled(False)
        self.trackBtn.clicked.connect(self.start_tracking)
        self.stopBtn.setEnabled(False)

        self.error = QErrorMessage()
        self.error.setWindowTitle("ERROR - Missing Data")

        self.timestr = ''
        self.log_iter = 0
        self.logfile = ''

        self.IMEI = ''
        self.email = ''
        self.e_pass = ''

        self.current = Updater(0, 0, 0, '', 0)

    def close_valve(self):
        e_thread = Emailer('close', self.IMEI)
        e_thread.start()
        print("closing valve")

    def attempt_cutdown(self):
        e_thread = Emailer('cutdown', self.IMEI)
        e_thread.start()

        print("attempting cutdown")

    def open_valve(self):
        e_thread = Emailer('open', self.IMEI)
        e_thread.start()
        print("opening valve")

    def send_idle(self):
        e_thread = Emailer('idle', self.IMEI)
        e_thread.start()
        print("sending idle command")

    # Takes the IMEI from the input box in the GUI, feeds it into a tracking thread, and enables the command buttons
    def start_tracking(self):
        if self.IMEIBox.text() == '':
            self.error.showMessage(
                'Please enter an IMEI before starting the tracker')
            self.error.setModal(True)
        else:
            try:
                self.log_iter = 0
                self.timestr = time.strftime("%Y_%m_%d")
                while os.path.exists("tracking CSVs/%s_tracking[%s].csv" % (self.timestr, self.log_iter)):
                    self.log_iter += 1
                self.logfile = open("tracking CSVs/%s_tracking[%s].csv" % (
                    self.timestr, self.log_iter), "w")
            except Exception as e:
                print("Tracking log file could not be created")
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.trackBtn.setEnabled(False)
            # self.openBtn.setEnabled(True) // Will be implemented at a later date
            # self.closeBtn.setEnabled(True)
            self.cdBtn.setEnabled(True)
            self.idleBtn.setEnabled(True)
            self.stopBtn.setEnabled(True)
            self.IMEI = self.IMEIBox.text()
            self.iridium_tracker = Iridium(

                self.db_host, self.db_user, self.db_passwd, self.db_name, self.IMEI)
            self.iridium_tracker.new_coords.connect(self.update_table)
            self.iridium_tracker.idle_send.connect(self.send_idle)
            self.stopBtn.clicked.connect(self.stop_tracking)
            self.iridium_tracker.start()

    def stop_tracking(self):
        self.trackBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.iridium_tracker.interrupt()
        self.iridium_tracker.__del__()

    # Takes the data sent by the tracking thread, and adds it to both the table and a .csv for archival purposes
    def update_table(self, coords):
        new_data = Updater(coords[0], coords[1],
                           coords[2], coords[3], coords[4])
        if new_data.get_lat() == 0.0 or new_data.get_lon() == 0.0 or new_data.get_alt() == 0.0:
            return

        if new_data.get_seconds() < self.current.get_seconds():
            return

        for item in coords:
            print(item)

        try:
            current_rows = self.tableWidget.rowCount()
            self.tableWidget.insertRow(current_rows)
            self.tableWidget.setItem(
                current_rows, 0, QTableWidgetItem(str(coords[0])))
            self.tableWidget.setItem(
                current_rows, 1, QTableWidgetItem(str(coords[1])))
            self.tableWidget.setItem(
                current_rows, 2, QTableWidgetItem(str(coords[2])))
            self.tableWidget.setItem(
                current_rows, 3, QTableWidgetItem(coords[3]))
            print("%s,%s,%s,%s\n" %
                  (str(coords[0]), str(coords[1]), str(coords[2]), coords[3]))
            self.logfile.write("%s,%s,%s,%s\n" %
                               (str(coords[0]), str(coords[1]), str(coords[2]), coords[3]))
            self.logfile.flush()
        except:
            print("ERROR: The location data could not be updated")

        self.current = new_data
        QApplication.processEvents()


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

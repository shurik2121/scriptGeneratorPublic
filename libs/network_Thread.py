import re
import subprocess
import threading
from PyQt5 import QtCore, QtGui


def ping_it(fgc, final_list):
    connection_res = []
    hostname = fgc.text()
    is_alive = subprocess.Popen(["ping", "-n", "1", hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print(is_alive)
    out, error = is_alive.communicate()
    #pattern = r"TTL"
    pattern = r"ms"
    #print(str(out))
    match = re.search(pattern, str(out))
    if match:
        connection_res = [fgc, 'color:green;']
    else:
        connection_res = [fgc, 'color:pink;']
    if connection_res not in final_list:
        final_list.append(connection_res)


class NetworkThread(QtCore.QThread):
    connection = QtCore.pyqtSignal(list)

    def __init__(self, fgc_list):

        QtCore.QThread.__init__(self)

        self.daemon = True
        self.fgc_list = fgc_list
        self.jobs = []
        self.final_list = []

    def run(self):
        try:
            for fgc in self.fgc_list:
                process = threading.Thread(target=ping_it, args=(fgc, self.final_list,))
                self.jobs.append(process)

            for j in self.jobs:
                j.start()

            for j in self.jobs:
                j.join()

        except ValueError:
            self.final_list = []
        self.connection.emit(self.final_list)

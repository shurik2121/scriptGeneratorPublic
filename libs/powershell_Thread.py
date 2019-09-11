import subprocess
import threading
from PyQt5 import QtCore

class powershellThread(QtCore.QThread):

    def __init__(self, powershellScript):

        QtCore.QThread.__init__(self)

        self.stdout = None
        self.stderr = None
        self.powershellScript = powershellScript
        #threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen([r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe', '-ExecutionPolicy', 'Unrestricted',self.powershellScript],
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        print('start runnnig powershell proccess: '+str(p))
        self.stdout, self.stderr = p.communicate()
        print('start runnnig powershell proccess2: ' + str(p.communicate()))
        print('information wait: ' + str(p.wait()))
        print('code oupput: ' + str(p.returncode))


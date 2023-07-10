# Import the necessary libraries
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from subprocess import Popen
import time

# Create a Windows service class
class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'MyService'
    _svc_display_name_ = 'My Service'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Your logic here
        self.is_alive = True
        Popen(['python', 'C:/Users/Baptiste/Downloads/flask_app/app.py'])
        while self.is_alive:
            time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)

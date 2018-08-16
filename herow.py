import sys

from PyQt5.QtCore import QThread, QUrl
from PyQt5.QtWidgets import QApplication
import kiwoomf

from flask import Flask, render_template



PORT = 5000
ROOT_URL = 'http://localhost:{}'.format(PORT)


class FlaskThread(QThread):
    def __init__(self, application):
        QThread.__init__(self)
        self.application = application
        self.api = kiwoomf.KiwoomF()

    def __del__(self):
        self.wait()

    def callback_connect(self):
        print('connected...')

    def connect(self):
        self.api.comm_connect(self.callback_connect)

    def run(self):
        self.application.run(port=PORT)


def provide_GUI_for(application):
    qtapp = QApplication(sys.argv)

    webapp = FlaskThread(application)
    webapp.start()

    qtapp.aboutToQuit.connect(webapp.terminate)

    return qtapp.exec_()


if __name__ == '__main__':
    from webapp.routes import app
    sys.exit(provide_GUI_for(app))
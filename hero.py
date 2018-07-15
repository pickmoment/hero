import sys
from PyQt5.QtWidgets import *

import kiwoomf

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 200, 300, 400)
        self.api = kiwoomf.KiwoomF()

        btnLogin = QPushButton("로그인", self)
        btnLogin.move(10, 10)
        btnLogin.clicked.connect(self.login_clicked)     

        btnCode = QPushButton("종목코드", self)
        btnCode.move(10, 40)
        btnCode.clicked.connect(self.code_clicked)   

    def login_clicked(self):
        self.api.comm_connect()

    def code_clicked(self):
        self.api.comm_terminate()
        # self.api.get_future_code_list('CL')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

class Hero(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slot()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slot(self):
        self.OnEventConnect.connect(self.event_connect)
        
    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.event_connect_loop = QEventLoop()
        self.event_connect_loop.exec_()

    def event_connect(self, err_code):
        if err_code == 0:
            print("로그인 성공")
        else:
            print("로그인 실패")
        self.event_connect_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        print(code_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hero = Hero()
    hero.comm_connect()
    hero.get_code_list_by_market('0')

    label = QLabel("Hello")
    label.show()

    app.exec_()
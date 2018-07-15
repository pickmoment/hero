import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

TR_REQ_TIME_INTERVAL = 5

class KiwoomF(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slot()

    def _create_kiwoom_instance(self):
        self.setControl("KFOPENAPI.KFOpenAPICtrl.1")

    def _set_signal_slot(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        
    def comm_connect(self):
        self.dynamicCall("CommConnect(1)")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()        

    def comm_terminate(self):
        self.dynamicCall("CommTerminate()")
        self.get_connect_state()

    def get_connect_state(self):
        state = self.dynamicCall("GetConnectState()")
        print('연결상태', state)

    def _event_connect(self, err_code):
        if err_code == 0:
            print("로그인 성공")
            self.get_connect_state()
        else:
            print("로그인 실패")
        
        self.login_event_loop.exit()

    def get_future_item_list(self):
        item_list = self.dynamicCall("GetGlobalFutureItemlist()")
        print(item_list)

    def get_future_code_list(self, item):
        code_list = self.dynamicCall("GetGlobalFutureCodelist(QString)", item)
        print(code_list)

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        # if rqname == "opt10060_req":
        #     self._opt10060(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass        
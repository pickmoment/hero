import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

TR_REQ_TIME_INTERVAL = 5

trcode_map = {
    'opc10001': {
        'name': '해외선물옵션틱차트조회',
        'items': ['체결시간','시가','고가','저가','현재가','거래량','영업일자'],
        'keys': ['dt','open','high','low','close','volume','day']
    },
    'opc10002': {
        'name': '해외선물옵션분차트조회',
        'items': ['체결시간','시가','고가','저가','현재가','거래량','영업일자'],
        'keys': ['dt','open','high','low','close','volume','day']
    },
    'opc10003': {
        'name': '해외선물옵션일차트조회',
        'items': ['일자','시가','고가','저가','현재가','거래량','영업일자'],
        'keys': ['dt','open','high','low','close','volume','day']
    }
}

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
        
    def comm_connect(self, callback):
        self._event_connect_callback = callback
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

        self._event_connect_callback(err_code)
        
        self.login_event_loop.exit()

    def get_future_item_list(self):
        item_list = self.dynamicCall("GetGlobalFutureItemlist()")
        print(item_list)

    def get_future_code_list(self, item):
        code_list = self.dynamicCall("GetGlobalFutureCodelist(QString)", item)
        print(code_list)

    def _set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def _comm_rq_data(self, trcode, next):
        rqname = trcode
        screen_no = trcode[-4:]
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _get_comm_data(self, code, record_name, index, item_name):
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", code,
                               record_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        data = self._read_tr_data(trcode, rqname)
        self._receive_tr_data_callback(data)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass        

    def _read_tr_data(self, trcode, rqname):
        conf = trcode_map[trcode]
        if conf:
            data_cnt = self._get_repeat_cnt(trcode, rqname)
            data = []
            for i in range(data_cnt):
                candle = {}
                for k in range(len(conf['items'])):
                    key = conf['keys'][k]
                    item = conf['items'][k]
                    candle[key] = self._get_comm_data(trcode, rqname, i, item)
                
                data.append(candle)
            return data

        return {}


    def get_ohlc(self, code, callback):
        self._receive_tr_data_callback = callback
        self._set_input_value('종목코드', code)
        self._set_input_value('시간단위', 60)
        self._comm_rq_data('opc10002', '')
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import kiwoomf
import entity

unit_map = {'분':'M', '틱':'T', '일':'D'}

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("main.ui", self)
        self.ui.show()
        self.api = kiwoomf.KiwoomF()
        self.ohlc_table_header = ['체결시간', '시가', '고가', '저가', '종가', '거래량', '영업일자']
        self.ohlc_data_list = []
        self.ohlc_table_model = BaseTableModel(self, self.ohlc_data_list, self.ohlc_table_header)
        self.tblOhlc.setModel(self.ohlc_table_model)

        self.ohlc_next = ''
        self.ohlc_timer = QTimer(self)
        self.ohlc_timer.timeout.connect(self.ohlc_timer_timeout)

        self.cbUnit.addItems(list(unit_map.keys()))

        self.code_info_map = {}

    def get_time_unit(self):
        unit = unit_map[self.cbUnit.currentText()]
        if unit == 'D':
            return unit
        return self.edTime.text() + unit

    def get_code_only(self, code):
        return code[:code.find('(')]

    def init_item_types(self):
        item_types = ['ENG(에너지)','CUR(통화)','IDX(지수)','MTL(금속)','INT(금리)','CMD(농산물)']
        self.cbItemTypes.clear()
        self.cbItemTypes.addItems(item_types)

    def init_engine(self, code, time_unit):
        self.engine = create_engine('sqlite:///db/{}_{}.db'.format(code.upper(), self.get_time_unit()))
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        entity.Base.metadata.create_all(self.engine)


    def ohlc_timer_timeout(self):
        if (len(self.edNext.text()) > 10):
            self.api.get_ohlc(self.edCode.text(), self.get_time_unit(), self.ohlc_callback, self.edNext.text())

    @pyqtSlot()
    def conjunction_changed(self):
        if self.ckConjunction.isChecked() and len(self.edCode.text()) >= 2:
            self.edCode.setText(self.edCode.text()[:2] + '000')
        else:
            self.edCode.setText(self.get_code_only(self.cbCodes.currentText()))

    @pyqtSlot()
    def codes_text_changed(self):
        self.edCode.setText(self.get_code_only(self.cbCodes.currentText()))

    def code_infos_callback(self, code_infos):
        self.code_info_map = code_infos
        items = ['{}({})'.format(key, self.code_info_map[key]['name']) for key in self.code_info_map]
        self.cbItems.addItems(items)

    @pyqtSlot()
    def item_types_text_changed(self):
        self.cbItems.clear()
        self.api.get_future_code_info_map(self.cbItemTypes.currentText()[:3], self.code_infos_callback)        

    @pyqtSlot()
    def items_text_changed(self):
        item = self.get_code_only(self.cbItems.currentText())
        if item:
            self.cbCodes.clear()
            codes = ['{}({})'.format(code['code'], code['name']) for code in self.code_info_map[item]['codes']]
            self.cbCodes.addItems(codes)

    @pyqtSlot()
    def edit_code_changed(self):
        self.edNext.setText("")

    @pyqtSlot()
    def connect_clicked(self):
        self.api.comm_connect(self.connect_callback)

    def connect_callback(self, err_code):
        if err_code == 0:
            self.btConnect.setText('연결됨')
            self.btConnect.setEnabled(False)
            self.init_item_types()
        else:
            print('connect', err_code)

    @pyqtSlot()
    def ohlc_clicked(self):
        if self.ohlc_timer.isActive():
            self.btOhlc.setStyleSheet("")
            self.ohlc_timer.stop()
        else:
            self.btOhlc.setStyleSheet("background-color: green;")
            self.init_engine(self.edCode.text(), self.get_time_unit())
            self.api.get_ohlc(self.edCode.text(), self.get_time_unit(), self.ohlc_callback, self.edNext.text())
            self.ohlc_timer.start(200)


    def ohlc_callback(self, result, next):
        self.ohlc_data_list = [list(r.values()) for r in result]
        self.ohlc_table_model = BaseTableModel(self, self.ohlc_data_list, self.ohlc_table_header)
        self.tblOhlc.setModel(self.ohlc_table_model)
        entity.Candle.add_list(self.session, result)
        self.session.commit()

        self.edNext.setText(next)



class BaseTableModel(QAbstractTableModel):
    def __init__(self, parent, rows, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.rows = rows
        self.header = header
    def rowCount(self, parent):
        return len(self.rows)
    def columnCount(self, parent):
        return len(self.header)
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.rows[index.row()][index.column()]
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.rows = sorted(self.rows,
            key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.rows.reverse()
        self.emit(SIGNAL("layoutChanged()"))        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


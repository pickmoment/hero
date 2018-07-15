import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt

import kiwoomf

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

    @pyqtSlot()
    def connect_clicked(self):
        self.api.comm_connect(self.connect_callback)

    def connect_callback(self, err_code):
        if err_code == 0:
            self.btConnect.setText('연결됨')
            self.btConnect.setEnabled(False)
        else:
            print('connect', err_code)

    @pyqtSlot()
    def ohlc_clicked(self):
        self.api.get_ohlc(self.edCode.text(), self.ohlc_callback)

    def ohlc_callback(self, result):
        self.ohlc_data_list = [list(r.values()) for r in result]
        print(self.ohlc_data_list)
        self.ohlc_table_model = BaseTableModel(self, self.ohlc_data_list, self.ohlc_table_header)
        self.tblOhlc.setModel(self.ohlc_table_model)


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


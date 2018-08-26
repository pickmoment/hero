# -*- coding: utf-8 -*-
import win32com.client
import time
import pythoncom
from enum import Enum
import datetime
# import os

class MarketType(Enum):
    INTERVAL = 0  #국내(주식,선물옵션)
    GLOBAL_STOCK = 1  #해외주식
    GLOBAL_DERIVATIVE = 2   #해외선물옵션
    INTERNAL_STOCK = 3    #국내 주식
    INTERVAL_KOSPIFUTURE = 4   #국내 코스피선물
    INTERVAL_KOSPIOPTION = 5   #국내 코스피옵션

DT_FORMAT = '%Y%m%d%H%M%S'
DAY_FORMAT = '%Y%m%d'
TIME_FORMAT = '%H%M%S'

def calculate_dt(basedate, basetime, unit):
    dt = basedate + basetime
    return dt

def calculate_start(basedate, basetime, unit):
    dt = basedate + basetime
    if unit == 'd':
        return dt
    elif unit[:1] == 'm':
        stamp = datetime.datetime.strptime(dt, DT_FORMAT) - datetime.timedelta(minutes=int(unit[1:]))
        return stamp.strftime(DT_FORMAT)
    elif unit[:1] == 't':
        return ''

def calculate_day(basedate, basetime, unit):
    dt = basedate + basetime
    if unit == 'd':
        return basedate
    elif unit[:1] in ('m', 't'):
        stamp = datetime.datetime.strptime(dt, DT_FORMAT)
        if stamp <= datetime.datetime.strptime(basedate + '070000', DT_FORMAT):
            return (stamp - datetime.timedelta(days=1)).strftime(DAY_FORMAT)
        return stamp.strftime(DAY_FORMAT)

class SessionEventHandler:
    def __init__(self):
        self.code = -1
        self.msg = None
        self.real = {}
        self.query = {}

    def reset(self):
        self.code = -1
        self.msg = None

    def OnLogin(self, result, msg):
        if result == 2:
            print('로그인 성공')
            self.code = result
            self.msg = None
        else:
            print('로그인 실패', result, msg)
            self.code = result
            self.msg = msg

    def OnReceiveError(self, req_id, err_code, msg):
        print('OnReceiveError', req_id, err_code, msg)
        self.code = 1
        self.msg = msg
	
    def OnReceiveData(self, req_id, tr_id):
        print('OnReceiveData', req_id, tr_id)
        if req_id not in self.query:
            self.query[req_id] = {}
        self.query[req_id][tr_id] = self.process_data(req_id, tr_id)
        print(self.query)
        self.code = 0
        self.msg = None

    def OnReceiveRealData(self, req_id, auto_id):
        print('OnReceiveRealData', req_id, auto_id)
        block = 'OutBlock1'
        jongcode = self.YOA_GetTRFieldString(auto_id, block, 'jongcode', 0)
        last = self.YOA_GetTRFieldString(auto_id, block, 'last', 0)
        print('jongcode: {}, last: {}'.format(jongcode, last))
        self.code = 0
        self.msg = None

    def OnReceiveSystemMessage(self, n_id, msg):
        print('SystemMessage', n_id, msg)

    def process_data(self, req_id, tr_id):
        results = []
        block = 'MSG'
        self.YOA_SetTRInfo(tr_id, block)
        count = self.YOA_GetRowCount(tr_id, block)
        for i in range(count-1):
            basedate = "{:06d}".format(self.YOA_GetFieldLong("basedate", i))
            basetime = "{:06d}".format(self.YOA_GetFieldLong("basetime", i))
            startjuka = self.YOA_GetFieldDouble("startjuka", i)
            highjuka = self.YOA_GetFieldDouble("highjuka", i)
            lowjuka = self.YOA_GetFieldDouble("lowjuka", i)
            lastjuka = self.YOA_GetFieldDouble("lastjuka", i)
            volume = self.YOA_GetFieldDouble("volume", i)
            results.append({
                'dt': calculate_dt(basedate, basetime, self.query[req_id]['unit']),
                'open': startjuka,
                'high': highjuka,
                'low': lowjuka,
                'close': lastjuka,
                'volume': volume,
                'dt_start': calculate_start(basedate, basetime, self.query[req_id]['unit']),
                'day': calculate_day(basedate, basetime, self.query[req_id]['unit'])
            })
        return results


class Session:
    def __init__(self):
        self.api = win32com.client.DispatchWithEvents("YuantaAPICOM.YuantaAPI", SessionEventHandler)

    def waiting(self):
        start = time.time()
        while self.api.code < 0:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.1)
            if time.time() - start > 5:
                return

    def login(self, id, pw, cert):
        self.api.reset()
        result = self.api.YOA_Login(id, pw, cert)
        if result != 1000:
            raise Exception('로그인 요청 실패')
        self.waiting()
        return self.api.code

    def connect(self, url, path):
        result = self.api.YOA_Initial(url, path)
        if result != 1000:
            raise Exception('연결 실패')
        print('연결 성공')
        return result

    def disconnect(self):
        result = self.api.YOA_UnInitial()
        print('연결해제', result)
        return result

    def accounts(self):
        accounts = []
        count = self.api.YOA_GetAccountCount()
        for i in range(count):
            account = self.api.YOA_GetAccount(i)
            account_name = self.api.YOA_GetAccountInfo(1, account)
            account_nick = self.api.YOA_GetAccountInfo(2, account)
            account_type = self.api.YOA_GetAccountInfo(3, account)
            accounts.append({'account': account, 'name': account_name, 'nick': account_nick, 'type': account_type})

        return accounts

    def codes(self):
        market_type = MarketType.GLOBAL_DERIVATIVE.value
        codes = []
        count = self.api.YOA_GetCodeCount(market_type)
        for i in range(count):
            cd = self.api.YOA_GetCodeInfoByIndex(market_type, 0, i)
            std_cd = self.api.YOA_GetCodeInfoByIndex(market_type, 1, i)
            name = self.api.YOA_GetCodeInfoByIndex(market_type, 2, i)
            eng_name = self.api.YOA_GetCodeInfoByIndex(market_type, 3, i)
            market = self.api.YOA_GetCodeInfoByIndex(market_type, 4, i)
            # if market == '111' and 'CL' in cd:  # 해외선물
            if market == '111':
                code = {'cd':cd, 'name':name}
                codes.append(code)

        return codes

    def chart(self, code, unit):
        self.api.reset()
        req_id = self.chart_call(code, unit)
        print(req_id)
        if req_id <= 1000:
            print('get_chart error', self.api.YOA_GetErrorMessage(self.api.YOA_GetLastError()))
            return []
        self.waiting()
        return self.get_query(req_id)

    def set_query(self, req_id, tr_id, unit):
        if req_id not in self.api.query:
            self.api.query[req_id] = {}
        self.api.query[req_id]['tr_id'] = tr_id
        self.api.query[req_id]['unit'] = unit

    def get_query(self, req_id):
        req = self.api.query[req_id]
        return req[req['tr_id']]

    def chart_call(self, code, unit):
        if unit == 'd':
            return self.chart_day(code)
        elif unit[:1] in ('m', 't'):
            return self.chart_time(code, unit)

    def chart_day(self, code):
        tr_id = '820101'
        self.api.YOA_SetTRInfo(tr_id, "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        self.api.YOA_SetFieldString("startdate", '', 0)
        self.api.YOA_SetFieldString("enddata", '', 0)
        self.api.YOA_SetFieldString("readcount", 500, 0)
        self.api.YOA_SetFieldString("link_yn", 'N', 0)
        req_id = self.api.YOA_Request(tr_id, True, -1)
        self.set_query(req_id, tr_id, 'd')
        return req_id            

    def chart_time(self, code, timeunit):
        now = datetime.datetime.now()
        tr_id = '820104' if timeunit[:1] == 'm' else '820106'
        self.api.YOA_SetTRInfo(tr_id, "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        self.api.YOA_SetFieldString("timeuint", timeunit[1:], 0)
        self.api.YOA_SetFieldString("startdate", '', 0)
        self.api.YOA_SetFieldString("starttime", '', 0)
        self.api.YOA_SetFieldString("enddate", now.strftime(DAY_FORMAT), 0)
        self.api.YOA_SetFieldString("endtime", now.strftime(TIME_FORMAT), 0)
        self.api.YOA_SetFieldString("readcount", 500, 0)
        self.api.YOA_SetFieldString("link_yn", 'N', 0)
        req_id = self.api.YOA_Request(tr_id, True, -1)
        self.set_query(req_id, tr_id, timeunit)
        return req_id

    def real_current(self, code):
        tr_id = '61'
        self.api.YOA_SetTRInfo(tr_id, "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        ret = self.api.YOA_RegistAuto(tr_id)
        return ret
        
if __name__ == '__main__':        
    url = 'simul.tradarglobal.api.com'
    path = 'c:/tools/YuantaAPI'

    session = Session()
    session.connect(url, path)
    session.login('moongux', 'gogo5', '')
    # print(session.real_current('ECU18'))
    # print(session.real_current('CLV18'))
    # while True:
    #     pythoncom.PumpWaitingMessages()
    #     time.sleep(1)
    # accounts = session.get_accounts()
    # print(accounts)
    # codes = session.get_codes(2)
    # [(lambda c: print(c))(code) for code in codes]
    # print(codes)
    session.chart('CLV18', 'd')
    session.disconnect()
    # session.clear()
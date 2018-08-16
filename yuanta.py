# -*- coding: utf-8 -*-
import win32com.client
import time
import pythoncom
# import os

class SessionEventHandler:
    def OnLogin(self, result, msg):
        if result == 2:
            print('로그인 성공')
        else:
            print('로그인 실패', result, msg)
        Session.change_running(False)

    def OnReceiveError(self, req_id, err_code, msg):
        print('OnReceiveError', req_id, err_code, msg)
        Session.change_running(False)    
	
    def OnReceiveData(self, req_id, dso_id):
        print('OnReceiveData', req_id, dso_id)
        Session.change_running(False)

    def OnReceiveRealData(self, req_id, auto_id):
        print('OnReceiveRealData', req_id, auto_id)
        Session.change_running(False)

    def OnReceiveSystemMessage(self, n_id, msg):
        print('SystemMessage', n_id, msg)

class Session:
    running = False

    def __init__(self, url, path):
        self.api = win32com.client.DispatchWithEvents("YuantaAPICOM.YuantaAPI", SessionEventHandler)
        result = self.api.YOA_Initial(url, path)
        if result != 1000:
            raise Exception('초기화 실패')
        print('초기화 성공')
    
    @classmethod
    def change_running(cls, running):
        cls.running = running

    def login(self, id, pw, cert):
        result = self.api.YOA_Login(id, pw, cert)
        self.change_running(True)
        if result != 1000:
            raise Exception('로그인 요청 실패')
        
        while self.running:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.2)

    def get_accounts(self):
        accounts = []
        count = self.api.YOA_GetAccountCount()
        for i in range(count):
            account = self.api.YOA_GetAccount(i)
            account_name = self.api.YOA_GetAccountInfo(1, account)
            account_nick = self.api.YOA_GetAccountInfo(2, account)
            account_type = self.api.YOA_GetAccountInfo(3, account)
            accounts.append({'account': account, 'name': account_name, 'nick': account_nick, 'type': account_type})

        return accounts

    def get_codes(self, market_type):
        codes = []
        count = self.api.YOA_GetCodeCount(market_type)
        for i in range(count):
            cd = self.api.YOA_GetCodeInfoByIndex(market_type, 0, i)
            std_cd = self.api.YOA_GetCodeInfoByIndex(market_type, 1, i)
            name = self.api.YOA_GetCodeInfoByIndex(market_type, 2, i)
            eng_name = self.api.YOA_GetCodeInfoByIndex(market_type, 3, i)
            market = self.api.YOA_GetCodeInfoByIndex(market_type, 4, i)
            if market == '111' and 'CL' in cd:  # 해외선물
                code = {'cd':cd, 'name':name}
                codes.append(code)

        return codes

    def get_chart(self, code, timeunit):
        self.api.YOA_SetTRInfo("820104", "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        self.api.YOA_SetFieldLong("timeunit", timeunit, 0)
        self.api.YOA_SetFieldLong("readcount", 100, 0)
        self.api.YOA_SetFieldString("link_yn", 'N', 0)
        result = self.api.YOA_Request("820104", True, -1)
        if result <= 1000:
            print('get_chart error', self.api.YOA_GetErrorMessage(self.api.YOA_GetLastError()))
        self.change_running(True)
        while self.running:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.2)

    def clear(self):
        self.api.YOA_UnInitial()



url = 'simul.tradarglobal.api.com'
path = 'c:/tools/YuantaAPI'

session = Session(url, path)
session.login('moongux', 'gogo5', '')
accounts = session.get_accounts()
print(accounts)
codes = session.get_codes(2)
print(codes)
session.get_chart('CLV18', 5)
session.clear()
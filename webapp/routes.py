from flask import Flask, render_template

import win32com.client

api = win32com.client.Dispatch("YuantaAPICOM.YuantaAPI")
URL = "simul.tradarglobal.api.com"
Path = "C:/tools/YuantaAPI"
result = api.YOA_Initial(URL, Path)
print('init:', result)
result = api.YOA_Login('moongux', 'gogo5', '')
print(result)

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello"
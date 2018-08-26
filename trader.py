from flask import Flask, render_template, jsonify
import yuanta

url = 'simul.tradarglobal.api.com'
path = 'c:/tools/YuantaAPI'

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello"

@app.route('/disconnect')
def disconnect():
    result = yuanta.disconnect()
    return 'disconnect: ' + str(result) 

@app.route('/accounts')
def accounts():
    result = yuanta.accounts()
    return 'accounts: ' + str(result)

@app.route("/codes")
def codes():
    result = yuanta.codes()
    return 'codes: ' + str(result)

@app.route('/chart/<code>/<unit>')
def chart(code, unit):
    result = yuanta.chart(code, unit)
    return jsonify(result)

if __name__ == "__main__":
    yuanta = yuanta.Session()
    result = yuanta.connect(url, path)
    result = yuanta.login('moongux', 'gogo5', '')
    app.run()

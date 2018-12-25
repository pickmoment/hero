from flask import Flask, render_template, jsonify
from flask import request as req
import yuanta

url = 'simul.tradarglobal.api.com'
path = 'c:/tools/YuantaAPI'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/disconnect')
def disconnect():
    result = yuanta.disconnect()
    return jsonify(result) 

@app.route('/accounts')
def accounts():
    result = yuanta.accounts()
    return jsonify(result)

@app.route("/codes")
def codes():
    result = yuanta.codes()
    return jsonify(result)

@app.route('/chart/<code>/<unit>', methods=['GET'])
def chart(code, unit):
    enddate = req.args.get('enddate')
    endtime = req.args.get('endtime')
    print('enddate:', enddate, 'endtime:', endtime)
    result = yuanta.chart(code, unit, enddate, endtime)
    return jsonify(result)

@app.route('/request/<req_id>')
def request(req_id):
    result = yuanta.request(req_id)
    return jsonify(result)

@app.route('/release/<req_id>')
def release(req_id):
    result = yuanta.release(req_id)
    return jsonify(result)

if __name__ == "__main__":
    yuanta = yuanta.Session()
    result = yuanta.connect(url, path)
    result = yuanta.login('moongux', 'gogo5', '')
    app.run(host='0.0.0.0')

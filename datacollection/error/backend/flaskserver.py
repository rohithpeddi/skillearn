from flask import Flask, request, jsonify

# This app runs on port 5000
app = Flask(__name__)

@app.route("/info")
def info():
	pass

@app.route("/record", methods=['POST'])
def record():
	recording_details = request.json
	pass

@app.route("/stop", methods=['POST'])
def stop():
	recording_details = request.json
	pass

@app.route("/upload", methods=['POST'])
def upload():
	recording_details = request.json
	pass

@app.route("/delete", methods=['POST'])
def delete():
	recording_details = request.json
	pass

if __name__=="__main__":
	app.run(host='0.0.0.0', debug=True)
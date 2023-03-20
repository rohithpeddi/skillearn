import logging
import os

from datacollection.user_app.backend.constants import *

from flask import Flask, request, jsonify

app = Flask(__name__)

if __name__ == "__main__":
	app.run(threaded=True, host='0.0.0.0', port=5000)

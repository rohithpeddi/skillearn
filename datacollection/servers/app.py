from flask import Flask
from service import *


app = Flask(__name__)


@app.route("/")
def main():
    return "Welcome!"



if __name__ == "__main__":
    app.run()
import os
from bottle import route, run

@route("/")
def hllo_world():
    return ""

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
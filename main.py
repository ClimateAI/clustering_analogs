import os

from flask import Flask
from flask import request

from clustering import get_analogs

app = Flask(__name__)
# https://analog-api-qh2dnfh7wa-uc.a.run.app/?lat=20.194824&lon=-100.9225607&k=6&quan=0.9
#lat, lon = 20.194824, -100.9225607
@app.route('/')
def analogs_api():
    lat = round(float(request.args.get('lat')),2)
    lon = round(float(request.args.get('lon')),2)
    k = int(request.args.get('k', None))
    quan = float(request.args.get('quan', None))
    return str(get_analogs(lat, lon, k, quan))

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080)))
from flask import Flask, request
import json
import hashlib
import hmac
import sys

app = Flask(__name__)

@app.route('/',methods = ['POST'])
def home():
    data = request.get_data()
    shopier_signature = request.headers['HTTP_SHOPIER_SIGNATURE']
    key = ''

    hash = hmac.new(key.encode(), data, hashlib.sha256).hexdigest()

    if hash != shopier_signature:
        return 'invalid request', 401

    shopier_account_id = request.headers['SHOPIER_ACCOUNT_ID']
    shopier_event = request.headers['SHOPIER_EVENT']
    array_data = json.loads(data)

    if shopier_event == 'order.created':
        order_id = array_data['id']
        order_status = array_data['status']
        first_name = array_data['shippingInfo']['firstName']
        last_name = array_data['shippingInfo']['lastName']
        # Proceed with the next steps your app may need.

        return 'success', 200
    return 'unsupported event', 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)

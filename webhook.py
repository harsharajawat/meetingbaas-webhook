from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

@app.route('/meetingbaas/webhook', methods=['GET', 'POST'])

def webhook():

    if request.method == 'GET':
        # Zoom webhook URL validation
        validation_token = request.args.get('validationToken')
        if validation_token:
            response = make_response(validation_token, 200)
            response.headers['Content-Type'] = 'text/plain'
            return response
        else:
            return "Missing validation token", 400
    data = request.json
    print('Received:', data)
    return {'status': 'received'}, 200

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)

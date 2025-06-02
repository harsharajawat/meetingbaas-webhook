from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/meetingbaas/webhook', methods=['POST'])
def webhook():

    if request.method == 'GET':
        return jsonify({'message': 'Zoom webhook verified'}), 200

    data = request.json
    print('Received:', data)
    return {'status': 'received'}, 200

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)

import hmac
import hashlib
import time
from flask import Flask, request, jsonify, abort

app = Flask(__name__)
ZOOM_WEBHOOK_SECRET = "Odgy7ir4R-uHMRs1wRB_0w"

def verify_zoom_signature(request):
    timestamp = request.headers.get('x-zm-request-timestamp')
    if not timestamp:
        print("Missing timestamp header")
        return False

    current_ts = int(time.time())
    req_ts = int(timestamp)
    if abs(current_ts - req_ts) > 300:
        print("Timestamp outside allowed range")
        return False

    body = request.get_data(as_text=True)
    message = f"v0:{timestamp}:{body}"

    computed_hash = hmac.new(
        ZOOM_WEBHOOK_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    expected_signature = f"v0={computed_hash}"
    received_signature = request.headers.get('x-zm-signature')

    print(f"Timestamp: {timestamp}")
    print(f"Expected Signature: {expected_signature}")
    print(f"Received Signature: {received_signature}")

    return hmac.compare_digest(expected_signature, received_signature)

@app.route('/meetingbaas/webhook', methods=['POST'])
def webhook():
    if not verify_zoom_signature(request):
        abort(401, description="Unauthorized request")

    data = request.json
    if not data:
        abort(400, description="Invalid JSON payload")

    event = data.get('event')
    if event == 'endpoint.url_validation':
        plain_token = data['payload']['plainToken']
        encrypted_token = hmac.new(
            ZOOM_WEBHOOK_SECRET.encode('utf-8'),
            plain_token.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return jsonify({
            'plainToken': plain_token,
            'encryptedToken': encrypted_token
        })

    print("Received Zoom event:", data)
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

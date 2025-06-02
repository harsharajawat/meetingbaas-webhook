import hmac
import hashlib
import time
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Replace this with your actual Zoom Webhook secret
ZOOM_WEBHOOK_SECRET = "Odgy7ir4R-uHMRs1wRB_0w"

def verify_zoom_signature(request):
    timestamp = request.headers.get('x-zm-request-timestamp')
    if not timestamp:
        return False

    # Prevent replay attacks
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

    print(f"[Zoom Signature] Expected: {expected_signature}")
    print(f"[Zoom Signature] Received: {received_signature}")

    return hmac.compare_digest(expected_signature, received_signature)

@app.route('/meetingbaas/webhook', methods=['POST'])
def zoom_webhook():
    data = request.get_json()

    # Handle initial Zoom URL validation (no signature verification needed)
    if data and data.get('event') == 'endpoint.url_validation':
        plain_token = data['payload']['plainToken']
        encrypted_token = hmac.new(
            ZOOM_WEBHOOK_SECRET.encode('utf-8'),
            plain_token.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        print("Handling Zoom URL validation...")
        return jsonify({
            'plainToken': plain_token,
            'encryptedToken': encrypted_token
        })

    # Verify signature for all other events
    if not verify_zoom_signature(request):
        abort(401, description="Unauthorized request")

    # Handle actual event data
    print("✅ Received Zoom Event:")
    print(data)

    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify
import uuid
import json
from datetime import datetime

app = Flask(__name__)

# In-memory storage for tabs (replace with database in production)
tabs = {}

@app.route('/tabs', methods=['POST'])
def create_tab():
    """
    Create a new browser tab
    Expected JSON: {
        "userId": "string",
        "sessionKey": "string (optional)",
        "url": "string (optional, defaults to about:blank)"
    }
    """
    data = request.get_json()
    
    if not data or 'userId' not in data:
        return jsonify({"error": "userId is required"}), 400
    
    user_id = data['userId']
    session_key = data.get('sessionKey', str(uuid.uuid4()))
    url = data.get('url', 'about:blank')
    
    # Generate tab ID
    tab_id = str(uuid.uuid4())
    
    # Store tab information
    tabs[tab_id] = {
        "tabId": tab_id,
        "userId": user_id,
        "sessionKey": session_key,
        "url": url,
        "title": "Loading...",
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "status": "created"
    }
    
    # In a real implementation, we would:
    # 1. Send instruction to worker pool to create actual tab
    # 2. Wait for confirmation from worker
    # 3. Then return the tab info
    
    # For now, simulate immediate creation
    tabs[tab_id]["status"] = "ready"
    tabs[tab_id]["title"] = "New Tab"
    
    return jsonify({
        "tabId": tab_id,
        "url": url,
        "title": "New Tab"
    }), 201

@app.route('/tabs/<tab_id>', methods=['GET'])
def get_tab(tab_id):
    """Get tab information"""
    if tab_id not in tabs:
        return jsonify({"error": "Tab not found"}), 404
    return jsonify(tabs[tab_id])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "whitehubs-api"})



@app.route('/tabs/<tab_id>/navigate', methods=['POST'])
def navigate_tab(tab_id):
    """
    Navigate tab to a URL
    Expected JSON: {
        "userId": "string",
        "url": "string",
        "waitUntil": "string (optional, defaults to 'networkidle')"
    }
    """
    if tab_id not in tabs:
        return jsonify({"error": "Tab not found"}), 404
    
    data = request.get_json()
    
    if not data or 'userId' not in data:
        return jsonify({"error": "userId is required"}), 400
    
    # Verify user owns this tab
    if tabs[tab_id]['userId'] != data['userId']:
        return jsonify({"error": "Unauthorized access to tab"}), 403
    
    url = data.get('url')
    wait_until = data.get('waitUntil', 'networkidle')
    
    if not url:
        return jsonify({"error": "url is required"}), 400
    
    # Update tab information
    tabs[tab_id]['url'] = url
    tabs[tab_id]['status'] = 'loading'
    tabs[tab_id]['lastActivity'] = datetime.utcnow().isoformat() + "Z"
    
    # In a real implementation, we would:
    # 1. Send navigation instruction to worker pool
    # 2. Worker would execute navigation in actual browser
    # 3. Update tab status based on worker feedback
    
    # Simulate navigation completion
    tabs[tab_id]['status'] = 'loaded'
    tabs[tab_id]['title'] = f"Page: {url}"  # Simplified
    
    return jsonify({
        "tabId": tab_id,
        "url": url,
        "title": tabs[tab_id]['title'],
        "status": "loaded"
    }), 200

@app.route('/tabs/<tab_id>/snapshot', methods=['GET'])
def get_tab_snapshot(tab_id):
    """
    Get accessibility snapshot of tab (with element refs)
    Query params: userId (required)
    """
    if tab_id not in tabs:
        return jsonify({"error": "Tab not found"}), 404
    
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId parameter is required"}), 400
    
    # Verify user owns this tab
    if tabs[tab_id]['userId'] != user_id:
        return jsonify({"error": "Unauthorized access to tab"}), 403
    
    # In a real implementation, we would:
    # 1. Request snapshot from worker pool
    # 2. Worker would return accessibility tree with element references
    
    # Simulate snapshot response
    snapshot = f"""[heading] Example Domain
[paragraph] This domain is for use in examples.
[link e1] More information...
[button e2] Accept Cookies
[input e3] Search field"""

    return jsonify({
        "tabId": tab_id,
        "snapshot": snapshot,
        "elements": {
            "e1": {"type": "link", "text": "More information...", "url": "https://iana.org/domains/example"},
            "e2": {"type": "button", "text": "Accept Cookies"},
            "e3": {"type": "input", "placeholder": "Search", "value": ""}
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

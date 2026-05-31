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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

#!/bin/bash
# Simple test for the API endpoint

echo "Starting API server in background..."
python3 /root/WhiteHubs/src/api/app.py &
API_PID=$!

# Give it a moment to start
sleep 3

echo "Testing tab creation endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:5000/tabs   -H "Content-Type: application/json"   -d '{"userId":"test-user","sessionKey":"test-session","url":"https://example.com"}')

echo "Response: $RESPONSE"

# Check if response contains expected fields
if echo "$RESPONSE" | grep -q '"tabId"' && echo "$RESPONSE" | grep -q '"url"'; then
    echo "✓ Tab creation endpoint working correctly"
else
    echo "✗ Tab creation endpoint not working as expected"
fi

# Clean up
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null
echo "API server stopped"

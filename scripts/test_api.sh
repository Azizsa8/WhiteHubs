#!/bin/bash
# Simple test for the API endpoints

echo "Starting API server in background..."
python3 /root/WhiteHubs/src/api/app.py > /tmp/api.log 2>&1 &
API_PID=$!

# Give it a moment to start
sleep 3

echo "Testing tab creation endpoint..."
CREATE_RESPONSE=$(curl -s -X POST http://localhost:5000/tabs   -H "Content-Type: application/json"   -d '{"userId":"test-user","sessionKey":"test-session","url":"https://example.com"}')

echo "Create Response: $CREATE_RESPONSE"

# Extract tabId from response using jq if available, otherwise use sed
if command -v jq >/dev/null 2>&1; then
    TAB_ID=$(echo "$CREATE_RESPONSE" | jq -r '.tabId')
else
    TAB_ID=$(echo "$CREATE_RESPONSE" | sed -n 's/.*"tabId":"\([^"]*\)".*/\1/p')
fi

if [ -z "$TAB_ID" ] || [ "$TAB_ID" = "null" ]; then
    echo "✗ Failed to create tab or extract tabId"
    echo "Response was: $CREATE_RESPONSE"
    kill $API_PID 2>/dev/null
    wait $API_PID 2>/dev/null
    exit 1
fi

echo "Created tab with ID: $TAB_ID"

echo "Testing tab navigation endpoint..."
NAVIGATE_RESPONSE=$(curl -s -X POST http://localhost:5000/tabs/$TAB_ID/navigate   -H "Content-Type: application/json"   -d '{"userId":"test-user","url":"https://google.com"}')

echo "Navigate Response: $NAVIGATE_RESPONSE"

# Check if navigation was successful (look for status containing "loaded")
if echo "$NAVIGATE_RESPONSE" | grep -q '"status".*loaded'; then
    echo "✓ Tab navigation endpoint working correctly"
else
    echo "✗ Tab navigation endpoint not working as expected"
    echo "Response was: $NAVIGATE_RESPONSE"
fi

echo "Testing tab snapshot endpoint..."
SNAPSHOT_RESPONSE=$(curl -s "http://localhost:5000/tabs/$TAB_ID/snapshot?userId=test-user")

echo "Snapshot Response: $SNAPSHOT_RESPONSE"

if echo "$SNAPSHOT_RESPONSE" | grep -q '"snapshot"'; then
    echo "✓ Tab snapshot endpoint working correctly"
else
    echo "✗ Tab snapshot endpoint not working as expected"
    echo "Response was: $SNAPSHOT_RESPONSE"
fi

# Clean up
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null
echo "API server stopped"

#!/bin/bash

echo "🚀 Testing SHIELD Scanner User Management API"
echo "============================================="
echo

# Test 1: Get Roles
echo "1️⃣  Testing GET /users/roles"
curl -s http://localhost:8000/users/roles | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    roles = data.get('data', [])
    print(f'   ✅ Found {len(roles)} roles: {[r[\"id\"] for r in roles]}')
except:
    print('   ❌ Failed to parse response')
"
echo

# Test 2: Get Stats  
echo "2️⃣  Testing GET /users/stats"
curl -s http://localhost:8000/users/stats | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    stats = data.get('data', {})
    print(f'   ✅ Stats: Total={stats.get(\"total\", 0)}, Active={stats.get(\"active\", 0)}, Inactive={stats.get(\"inactive\", 0)}')
    print(f'   📊 By Role: {stats.get(\"byRole\", {})}')
except Exception as e:
    print(f'   ❌ Failed: {e}')
"
echo

# Test 3: Create User
echo "3️⃣  Testing POST /users"
RESPONSE=$(curl -s -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com", "fullname": "Test User", "role": "Developer", "namespaces": ["cluster-dev:development"]}')

echo "$RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'data' in data:
        user = data['data']
        print(f'   ✅ Created user: {user[\"email\"]} (ID: {user[\"id\"]})')
        # Save user ID for further tests
        with open('/tmp/test_user_id.txt', 'w') as f:
            f.write(user['id'])
    elif 'detail' in data:
        if 'already in use' in str(data['detail']):
            print('   ⚠️  User already exists (email conflict)')
        else:
            print(f'   ❌ Error: {data[\"detail\"]}')
    else:
        print(f'   ❌ Unexpected response: {data}')
except Exception as e:
    print(f'   ❌ Failed to parse: {e}')
    print(f'   Raw response: {sys.stdin.read()[:200]}...')
"
echo

# Test 4: List Users
echo "4️⃣  Testing GET /users"
curl -s "http://localhost:8000/users?limit=5" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'data' in data:
        users = data['data']['users']
        pagination = data['data']['pagination']
        print(f'   ✅ Found {len(users)} users (Total: {pagination[\"total\"]})')
        for user in users[:3]:  # Show first 3
            print(f'      👤 {user[\"fullname\"]} ({user[\"email\"]}) - {user[\"role\"]}')
    else:
        print(f'   ❌ Unexpected response structure')
except Exception as e:
    print(f'   ❌ Failed: {e}')
"
echo

echo "🎉 User Management API Test Complete!"
echo
echo "📖 Full API documentation available at: http://localhost:8000/docs"
echo "🔗 User management endpoints: http://localhost:8000/users/*"

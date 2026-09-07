#!/bin/bash
# =========================================================
#  MCP server quick test — server chal raha ho tab chalana:
#  bash test-mcp.sh
# =========================================================
URL="http://localhost:3000"

echo "--- 1. list_files ---"
curl -s -m 10 -X POST $URL -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_files","arguments":{}}}'; echo
echo "--- 2. write_file phone-test.txt ---"
curl -s -m 10 -X POST $URL -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"write_file","arguments":{"path":"phone-test.txt","content":"phone se test OK"}}}'; echo
echo "--- 3. read_file phone-test.txt ---"
curl -s -m 10 -X POST $URL -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"read_file","arguments":{"path":"phone-test.txt"}}}'; echo
echo "--- 4. delete_file phone-test.txt ---"
curl -s -m 10 -X POST $URL -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"delete_file","arguments":{"path":"phone-test.txt"}}}'; echo
echo "--- 5. final list ---"
curl -s -m 10 -X POST $URL -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"list_files","arguments":{}}}'; echo
echo "SAB JAWAB AA GAYE = SERVER OK!"

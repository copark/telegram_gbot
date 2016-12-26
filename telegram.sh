SERVER=https://localhost
echo curl -X GET $SERVER/set-webhook?url=$SERVER/webhook -v
curl $SERVER/set-webhook?url=$SERVER/webhook -v

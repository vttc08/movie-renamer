source .env
curl -X POST ''$OLIVETIN_URL'/api/StartAction' -d '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": "'"'$1'"'"}]}'

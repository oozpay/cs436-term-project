#!/bin/bash

FILE=~/message-logger/messages.log
BUCKET=webchat-backups-1
OBJECT=messages.log

curl -X PUT --data-binary @"$FILE" \
  -H "Content-Type: text/plain" \
  "https://storage.googleapis.com/$BUCKET/$OBJECT"

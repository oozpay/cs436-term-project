#!/bin/bash

FILE=~/message-logger/messages.log
BUCKET=webchat-backups-1
OBJECT=messages.log  # you can make this dynamic with timestamp if you want

curl -X PUT --data-binary @"$FILE" \
  -H "Content-Type: text/plain" \
  "https://storage.googleapis.com/$BUCKET/$OBJECT"
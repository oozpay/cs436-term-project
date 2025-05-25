#!/bin/bash

FILE=~/message-logger/messages.log
BUCKET=[BUCKET_NAME] # insert actual bucket name here
OBJECT=messages.log

curl -X DELETE "https://storage.googleapis.com/$BUCKET/$OBJECT"

curl -X PUT --data-binary @"$FILE" \
  -H "Content-Type: text/plain" \
  "https://storage.googleapis.com/$BUCKET/$OBJECT"

Steps to recreate the cloud-native architecture:

NOTE 1: Replace all placeholders in square brackets (e.g., `[PROJECT_ID]`) with your actual values.
NOTE 2: Docker Desktop and gcloud CLI must be installed and running for deployment.
NOTE 3: Some commands should be run in your local terminal within the project directory, while others should be executed in the Cloud Shell terminal. Refer to the instructions in each step for guidance.

GKE cluster setup:

1) Locate "GKE webchat server" folder and authenticate GCP account in local terminal:
gcloud auth login
gcloud config set project [PROJECT_ID] 
gcloud config set compute/zone us-central1-a 

2) Create cluster in cloud shell terminal:
gcloud container clusters create webchat-cluster \
  --zone=us-central1-a \
  --enable-ip-alias \
  --num-nodes=1 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=3

3) Enable artifact registry and create and artifact registry in cloud shell terminal:
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create webchat-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Webchat container repo"

4) Get cluster credentials in local terminal:
gcloud container clusters get-credentials webchat-cluster

5) Authenticate Docker to push, then build and push the Docker image in local terminal:
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/[PROJECT_ID]/webchat-repo/webchat-app:latest .
docker push us-central1-docker.pkg.dev/[PROJECT_ID]/webchat-repo/webchat-app:latest

6) Apply Kubernetes manifests in local terminal:
kubectl apply -f redis.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

7) To access the webchat app, get External IP for the service in local terminal and paste it in browser:
kubectl get service webchat-service



Compute Engine VM setup:

1) Create a VM instance in Compute Engine:
Name: message-logger-vm
Region/Zone: us-central1-a
Machine type: e2-micro
Boot disk: Ubuntu 22.04 LTS x86/64 (amd64)
HTTP traffic: Allowed

2) Install Node.js on the VM:
sudo apt-get update
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node -v

3) Create a Simple Message Logger Server on the VM:
mkdir message-logger
cd message-logger
nano server.js

CODE FOR server.js (can be found in "VM scripts" folder):
const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(express.json());
const logFilePath = path.join(__dirname, 'messages.log');
app.get('/', (req, res) => {
  res.send('Logger server is running.');
});
app.post('/store-message', (req, res) => {
  const { user, msg, timestamp } = req.body;
  const line = `${timestamp} [${user}]: ${msg}\n`;
  fs.appendFile(logFilePath, line, (err) => {
    if (err) {
      console.error('Failed to save message:', err);
      return res.status(500).send('Error saving message');
    }
    console.log('Message saved:', line.trim());
    res.sendStatus(200);
  });
});
const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Logger server listening on port ${PORT}`);
});

4) Install Express in the message-logger directory and run the server:
npm init -y
npm install express
node server.js

5) Allow Firewall Access to Port 3001 in Google Cloud Console
-Go to VPC Network > Firewall Rules
-Click Create Firewall Rule
Configurations:
	-Name: allow-logger-port
	-Targets: All instances in the network
	-Source IP ranges: 0.0.0.0/0
	-Protocols and ports: Check Specified protocols, select TCP, and enter 3001

6) get the External IP of message-logger-vm and replace [VM-IP] with that IP address in the server.js file in the "GKE webchat server" folder. relevant section in server.js listed below:
socket.on('send message', async (msg) => {
  const messagePayload = {
    user: socket.username,
    msg: msg,
    timestamp: new Date().toISOString()
  };

  try {
    await axios.post('http://[VM-IP]:3001/store-message', messagePayload); <------- insert IP address here
  } catch (err) {
    console.error('Failed to store message:', err.message);
  }

  io.emit('new message', messagePayload);
});

7) create a bucket in google cloud in cloud shell terminal and grant permissions for bucket:
gsutil mb -p webchat-gke -l us-central1 gs://webchat-backups-1
gsutil uniformbucketlevelaccess set on gs://webchat-backups-1
gsutil iam ch allUsers:objectCreator gs://webchat-backups-1
gsutil iam ch allUsers:objectViewer gs://webchat-backups-1

8) create a shell script in VM to upload logs to bucket:
nano upload-log.sh

SCRIPT CODE:
#!/bin/bash
FILE=~/message-logger/messages.log
BUCKET=webchat-backups-1
OBJECT=messages.log  # you can make this dynamic with timestamp if you want
curl -X PUT --data-binary @"$FILE" \
  -H "Content-Type: text/plain" \
  "https://storage.googleapis.com/$BUCKET/$OBJECT"

8) make the script executable in VM:
chmod +x /home/[USER]/upload-log.sh

9) automate script in VM:
crontab -e
add this line: 0 * * * * /home/[USER]/upload-log.sh 



Serverless function setup:

1) Enable Cloud Functions and Cloud Storage APIs in cloud shell terminal:
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable storage.googleapis.com

2) locate "serverless logging and backup funcion" folder and deploy in local terminal:
gcloud functions deploy backupLog --runtime nodejs18 --trigger-resource webchat-backups-1 --trigger-event google.storage.object.finalize --entry-point backupLog --region us-central1-a

3) verify deployment:
gcloud functions logs read backupLog --region us-central1-a



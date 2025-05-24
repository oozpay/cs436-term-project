
# Project Structure:
```
├── GKE webchat server				# server application front/backend and K8S manifests
├── VM scripts         				# scripts used in the vm
├── Locust load test scripts       		# load test script
├── serverless logging and backup function	# serverless function script
```

# Steps to recreate the cloud-native architecture:

### NOTE 1: Replace all placeholders in square brackets (e.g., `[PROJECT_ID]`) with your actual values.
### NOTE 2: Docker Desktop and Cloud SDK must be installed and running for deployment.
### NOTE 3: Some commands should be run in your local terminal within the project directory, while others should be executed in the Cloud Shell terminal. Refer to the instructions in each step for guidance.

## GKE cluster setup:

### 1) Locate `GKE webchat server` folder and authenticate GCP account in local terminal:
```
gcloud auth login
gcloud config set project [PROJECT_ID] 
gcloud config set compute/zone us-central1-a 
```

### 2) Create cluster in cloud shell terminal:
```
gcloud container clusters create webchat-cluster \
  --zone=us-central1-a \
  --enable-ip-alias \
  --num-nodes=1 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=3
```

### 3) Enable artifact registry and create and artifact registry in cloud shell terminal:
```
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create webchat-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Webchat container repo"
```

### 4) Get cluster credentials in local terminal:
`gcloud container clusters get-credentials webchat-cluster`

### 5) Authenticate Docker to push, then build and push the Docker image in local terminal:
```
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/[PROJECT_ID]/webchat-repo/webchat-app:latest .
docker push us-central1-docker.pkg.dev/[PROJECT_ID]/webchat-repo/webchat-app:latest
```

### 6) Apply Kubernetes manifests in local terminal:
```
kubectl apply -f redis.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

### 7) To access the webchat app, get External IP for the service in local terminal and paste it in browser:
`kubectl get service webchat-service`



## Compute Engine VM setup:

### 1) Create a VM instance in Compute Engine:
Name: message-logger-vm
Region/Zone: us-central1-a
Machine type: e2-micro
Boot disk: Ubuntu 22.04 LTS x86/64 (amd64)
HTTP traffic: Allowed

### 2) Install Node.js on the VM:
```
sudo apt-get update
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node -v
```

### 3) Create a Simple Message Logger Server on the VM:
```
mkdir message-logger
cd message-logger
nano server.js
```

CODE FOR `server.js` CAN BE FOUND IN `VM scripts` FOLDER

### 4) Install Express in the message-logger directory and run the server:
```
npm init -y
npm install express
node server.js
```

### 5) Allow Firewall Access to Port 3001 in Google Cloud Console
-Go to VPC Network > Firewall Rules
-Click Create Firewall Rule
Configurations:
	-Name: allow-logger-port
	-Targets: All instances in the network
	-Source IP ranges: 0.0.0.0/0
	-Protocols and ports: Check Specified protocols, select TCP, and enter 3001

### 6) In the `server.js` file located in the "GKE webchat server" folder, replace `[IP]` in the line `await axios.post('http://[IP]:3001/store-message', messagePayload);` with the External IP address of the `message-logger-vm` instance (keep the port number as 3001)

### 7) create a bucket in google cloud in cloud shell terminal and grant permissions for bucket:
```
gsutil mb -p [PROJECT_ID] -l us-central1 gs://webchat-backups-1
gsutil uniformbucketlevelaccess set on gs://webchat-backups-1
gsutil iam ch allUsers:objectCreator gs://webchat-backups-1
gsutil iam ch allUsers:objectViewer gs://webchat-backups-1
```

### 8) create a shell script in VM home directory to upload logs to bucket:
`nano upload-logs.sh`

CODE FOR `upload-logs.sh` CAN BE FOUND IN `VM scripts` FOLDER


### 9) make the script executable in VM:
`chmod +x /home/[USER]/upload-logs.sh`

### 10) automate script in VM using cron command-line utility:
`crontab -e`

add this line to schedule hourly backups: 
`0 * * * * /home/[USER]/upload-logs.sh`



## Serverless function setup:

### 1) Enable Cloud Functions and Cloud Storage APIs in cloud shell terminal:
```
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable storage.googleapis.com
```

### 2) locate `serverless logging and backup funcion` folder and deploy in local terminal:
```
gcloud functions deploy backupLog --runtime nodejs18 --trigger-resource webchat-backups-1 --trigger-event google.storage.object.finalize --entry-point backupLog --region us-central1-a
```

### 3) verify deployment:
`gcloud functions logs read backupLog --region us-central1-a`



## Locust load test:

### 1) Locate `locust load test script` folder

### 2) replace the IP address in the line `self.sio.connect("http://[IP]")` with `webchat-service`'s external IP (port number isn't necessary since it will automatically use port 80)

### 3) run the script in local terminal:
`locust -f locustfile.py`

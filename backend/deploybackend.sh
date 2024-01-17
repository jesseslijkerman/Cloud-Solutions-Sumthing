#!/bin/bash

# Define variables
PROJECT_ID="hbo-ict-pr-gr-1"
CLUSTER_NAME="sumthing-test"
REGION="europe-west4"
IMAGE_NAME="sumthing-backend"

# Authorize using service account key 
gcloud auth activate-service-account --key-file 'C:\Users\jesse\AppData\Local\Google\Cloud SDK\hbo-ict-pr-gr-1-6c1089826d32.json'

# Create Kubernetes cluster
gcloud container --project "$PROJECT_ID" clusters create-auto "$CLUSTER_NAME" --region "$REGION" --release-channel "regular" --network "projects/$PROJECT_ID/global/networks/default" --subnetwork "projects/$PROJECT_ID/regions/$REGION/subnetworks/default" --cluster-ipv4-cidr="10.1.0.0/17"

# Configure kubectl to cluster
gcloud container clusters get-credentials "$CLUSTER_NAME" --region "$REGION"

# Authenticate Docker to GCR
gcloud auth configure-docker

# Tag your Docker image
docker tag cloud-solutions-sumthing "gcr.io/$PROJECT_ID/$IMAGE_NAME"

# Push the Docker image to GCR
docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME"

# Apply Kubernetes deployment
kubectl apply -f deployment.yaml

# Expose the deployment
kubectl expose deployment "$CLUSTER_NAME" --type=LoadBalancer --port=80 --target-port=5000

# Get the external IP
kubectl get services


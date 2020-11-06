#!/bin/bash
gcloud builds submit --tag gcr.io/climate-ai/analog-api
gcloud run deploy analog-api --image gcr.io/climate-ai/analog-api --platform managed --memory 1024 --region us-central1
gcloud run services update-traffic analog-api --to-revisions=LATEST=100 --region us-central1 --platform managed
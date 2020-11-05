#!/bin/bash
gcloud builds submit --tag gcr.io/climate-ai/analogs-api
gcloud run deploy analogs-api --image gcr.io/climate-ai/analogs-api --platform managed --memory 1024 --region us-central1
gcloud run services update-traffic analogs-api --to-revisions=LATEST=100 --region us-central1 --platform managed
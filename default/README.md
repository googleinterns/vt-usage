# Default App

The app runs VTI (VirusTotal Intelligence) query every hour by cron and sends the results to the webhook app. 

## Data

VT API key, VTI query and webhook URL are submitted by user via web form and stored in Google Cloud Datastore.

## Authentication

Authorization to webhook is done using private API key (stored in Cloud Secret Manager). The app first authorizes to webhook, receives JWT token, and then adds this token to its data sending requests.

## Deployment

There are _app.yaml_ configuration file and _cron.yaml_ for configuring cron that are being used for deployment to Google App Engine. Deploy can be done using 
```
gcloud app deploy
```

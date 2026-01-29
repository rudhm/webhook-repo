# GitHub Webhook Receiver Dashboard

This app uses Flask to receive GitHub webhooks.
It saves events in MongoDB and shows them on a live dashboard.

**Status:** Done (includes Merge events)

## Features

* Updates every 15 seconds
* Saves all events in MongoDB
* Supports:

  * PUSH (commits)
  * PULL REQUEST (new PR)
  * MERGE (merged PR)

## Requirements

* Python 3
* MongoDB (running on your computer)
* Ngrok

## Install

```bash
git clone <your-repo-link>
cd webhook-repo
pip install Flask Flask-PyMongo
```

## Run

1. Start MongoDB

```bash
mongod --dbpath ./data/db
```

2. Start the app

```bash
python run.py
```

Open: [http://localhost:5000](http://localhost:5000)

3. Start ngrok (new terminal)

```bash
ngrok http 5000
```

Copy the HTTPS link.

4. Set GitHub Webhook

* Repo → Settings → Webhooks
* Payload URL: `<ngrok-url>/webhook/receiver`
* Content type: `application/json`
* Events: Pushes and Pull requests

## Use

Open:
[http://localhost:5000/webhook/](http://localhost:5000/webhook/)

Do pushes or PRs in the repo to see live updates.

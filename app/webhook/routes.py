from flask import Blueprint, json, request, render_template
from app.extensions import mongo
from datetime import datetime # Required for date formatting

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

# 1. ROUTE FOR THE UI
@webhook.route('/')
def dashboard():

     # get latest 10 events
    events = list(mongo.db.events.find().sort("timestamp", -1).limit(10))

    # Loop through each event to prepare UI text
    for event in events:
        ts = event.get("timestamp")
        try:
            # Format the timestamp into readable form
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            pretty_time = dt.strftime("%d %B %Y - %I:%M %p UTC")
        except:
            # If timestamp is missing or badly formatted,
            # just use the original value so app does not crash
            pretty_time = ts

        # If any field is missing, provide safe default
        author = event.get("author", "Unknown")
        to_branch = event.get("to_branch", "unknown")
        from_branch = event.get("from_branch", "unknown")

        # Get action type
        action = event.get("action")
        if action == "PUSH":
            event["ui_message"] = f'"{author}" pushed to "{to_branch}" on {pretty_time}'
        elif action == "PULL_REQUEST":
            event["ui_message"] = f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {pretty_time}'
        elif action == "MERGE":
            event["ui_message"] = f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {pretty_time}'
        else:
            event["ui_message"] = f'{action} by {author} on {pretty_time}'
    
    # Send events to HTML template for display
    return render_template('index.html', events=events)

# 2. ROUTE FOR GITHUB (WEBHOOK)
@webhook.route('/receiver', methods=["POST"])
def receiver():
    # Get the data sent by github
    data = request.json

    event_type = request.headers.get("X-Github-Event")

    # We will fill this dict with our data
    info = {}

    # CASE 1: SOMEONE PUSHED CODE
    if event_type == "push":
        info["action"] = "PUSH"
        info["author"] = data["pusher"]["name"]
        info["request_id"] = data["head_commit"]["id"]

        # Github sends "refs/heads/master", we just want "master"
        branch_name = data["ref"].split('/')[-1]
        info["from_branch"] = branch_name
        info["to_branch"] = branch_name
        info["timestamp"] = data["head_commit"]["timestamp"]

    # CASE 2: PULL REQUEST (OR MERGE)
    elif event_type == "pull_request":
        pr = data["pull_request"] # Extract pr data for better readability

        # Check if it is a merge or just a pr 
        if data["action"] == "closed" and pr["merged"] is True:
            info["action"] = "MERGE"
        else:
            info["action"] = "PULL_REQUEST"

        info["author"] = pr["user"]["login"]
        info["request_id"] = str(pr["id"])
        info["from_branch"] = pr["head"]["ref"]
        info["to_branch"] = pr["base"]["ref"]
        info["timestamp"] = pr["updated_at"]
    
    # Save to Database
    # Only save if we actually found data
    if info:
        print(f"Saving: {info}")
        mongo.db.events.insert_one(info)

    #print(f"Received Webhook Data:")
    #print(json.dumps(payload, indent=4))

    return {}, 200

import os

from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

# Initialize Slack app and request handler
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
handler = SlackRequestHandler(app)

api = FastAPI()


# 1. Standard Slack Events endpoint
@api.post("/slack/events")
async def endpoint(req: Request):
  return await handler.handle(req)


# 2. Your custom endpoint
@api.get("/custom-route")
def custom_endpoint():
  return {"message": "This is a custom endpoint!"}


@app.message("hello")
def handle_message(message, say):
  say(f"Hi <@{message['user']}>!")

import utils
import uvicorn
from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from sqlmodel import Session, select
import models
import settings

prefix = settings.SLACK_COMMAND_PREFIX

# Initialize Slack app and request handler
app = App(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
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


@app.command(f"/{prefix}linkbot")
def linkbot(ack, respond, command):
    ack()
    user_id = command.get("user_id")
    text_args = command.get("text")
    if not text_args:
        with Session(models.engine) as session:
            while True:
                token = utils.generate_token()
                existing = session.exec(
                    select(models.PendingAccountLink).where(
                        models.PendingAccountLink.token == token
                    )
                ).first()
                if not existing:
                    break

        respond(f"Hi <@{user_id}>!\n\nRun this command on your alt to link it:\n\n```{command['command']} {token}```")


if __name__ == "__main__":
    # Start the Uvicorn server programmatically
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

from fastapi.responses import RedirectResponse
import uvicorn
from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from sqlmodel import Session, select

import models
import settings
import utils

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

@api.get("/")
def redirect_to_github():
    return RedirectResponse("https://github.com/KavyanshKhaitan2/slack-linkbot")

# 2. Your custom endpoint
@api.get("/check")
def custom_endpoint(slack_id):
    with Session(models.engine) as session:
        existing = session.exec(
            select(models.AccountLink).where(
                models.AccountLink.child_slack_id == slack_id
            )
        ).first()
        if existing:
            return {
                "is_alt": True,
                "verification_status": utils.check_verification_status(slack_id),
                "is_verified": utils.is_verified(slack_id),
                "object": existing,
            }
        else:
            return {
                "is_alt": False,
                "verification_status": utils.check_verification_status(slack_id),
                "is_verified": utils.is_verified(slack_id),
                "object": None,
            }


@app.message("hello")
def handle_message(message, say):
    say(f"Hi <@{message['user']}>!")


@app.command(f"/{prefix}linkbot")
def linkbot(ack, respond, command):
    ack()
    user_slack_id = command.get("user_id")
    text_args = command.get("text")
    if not text_args:
        with Session(models.engine) as session:
            existing_links = session.exec(
                select(models.PendingAccountLink).where(
                    models.PendingAccountLink.parent_slack_id == user_slack_id
                )
            ).all()
            for link in existing_links:
                respond(
                    f"_Your previous link with token *`{link.token}`* has been revoked!_"
                )
                session.delete(link)
            session.commit()
            while True:
                token = utils.generate_token()
                existing = session.exec(
                    select(models.PendingAccountLink).where(
                        models.PendingAccountLink.token == token
                    )
                ).first()
                if not existing:
                    break
            pending_link = models.PendingAccountLink(
                parent_slack_id=user_slack_id, token=token
            )
            session.add(pending_link)
            session.commit()

        respond(
            f"Hi <@{user_slack_id}>!\n\nRun this command on your alt to link it:\n```{command['command']} {token}```\nDo not share this code with anyone else!\nRun *`{command['command']}`* again to revoke this token."
        )
        return

    with Session(models.engine) as session:
        link = session.exec(
            select(models.PendingAccountLink).where(
                models.PendingAccountLink.token == text_args
            )
        ).first()

    if not link:
        return respond(
            f"Pending link with this token not found!\n\n_Run *`/{prefix}linkbot`* on your main account to issue a new token!_"
        )
    if user_slack_id == link.parent_slack_id:
        return respond(
            "You cant link your account to yourself, silly!\n\nTry running this on your alt!"
        )

    if utils.is_verified(user_slack_id):
        return respond("You are verified, and not an alt account!")

    respond(
        text=f"Are you sure you wanna link this account to <@{link.parent_slack_id}>?",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Are you sure you wanna link this account to <@{link.parent_slack_id}> as an alt?\n\n_Please cancel this action if you did not request it!_",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Yes, link"},
                        "style": "primary",
                        "action_id": "confirm_link",
                        "value": link.token,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Cancel"},
                        "action_id": "cancel_link",
                        "value": link.token,
                    },
                ],
            },
        ],
    )


@app.action("confirm_link")
def confirm_link(ack, body, respond):
    ack()
    clicker_id = body["user"]["id"]
    token = body["actions"][0]["value"]

    with Session(models.engine) as session:
        pending = session.exec(
            select(models.PendingAccountLink).where(
                models.PendingAccountLink.token == token
            )
        ).first()

        if not pending:
            return respond(
                text="This link request expired or was already used.",
                replace_original=True,
            )
        if utils.is_verified(clicker_id):
            return respond("You are verified, and not an alt account!")

        if pending.parent_slack_id == clicker_id:
            return respond(
                text="You can't link your account to yourself!", replace_original=True
            )

        existing = session.exec(
            select(models.AccountLink).where(
                models.AccountLink.child_slack_id == clicker_id
            )
        ).first()

        if existing:
            return respond(
                text=f"This account has already been linked to <@{existing.parent_slack_id}>. You cant relink it again!",
                replace_original=True,
            )

        app.client.chat_postMessage(
            channel=pending.parent_slack_id,
            text=f"<@{clicker_id}> has been linked as an alt.",
        )

        session.add(
            models.AccountLink(
                parent_slack_id=pending.parent_slack_id,
                child_slack_id=clicker_id,
            )
        )
        session.delete(pending)  # single-use token
        session.commit()

    respond(
        text=f"Linked! This account is now an alt of <@{pending.parent_slack_id}>.",
        replace_original=True,
    )


@app.action("cancel_link")
def cancel_link(ack, body, respond):
    ack()

    clicker_id = body["user"]["id"]
    token = body["actions"][0]["value"]

    with Session(models.engine) as session:
        pending = session.exec(
            select(models.PendingAccountLink).where(
                models.PendingAccountLink.token == token
            )
        ).first()
        if not pending:
            return respond(text="Token expired", replace_original=True)

        app.client.chat_postMessage(
            channel=pending.parent_slack_id,
            text=f"<@{clicker_id}> clicked cancel.\n\nYour token has been revoked.",
        )

        session.delete(pending)
        session.commit()
    respond(
        text="Cancelled and revoked token. No accounts were linked.",
        replace_original=True,
    )


if __name__ == "__main__":
    # Start the Uvicorn server programmatically
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# Linkbot for Slack
Isn't it annoying when you wanna check if someone is an alt on Slack?
Use this to check if they are an alt!

## Contents
- [Usage](#usage)
- 1. [`/linkbot` command](#1.-`/linkbot`-command)
- 2. [`/check` endpoint](#2.-`/check`-endpoint)
- [Setup & Deployment](#setup--deployment)

## Usage
### 1. `/linkbot` command
In slack, run `/linkbot` on your main account and you get a code to run on your alt.

Running that code on your alt links them together.
### 2. `/check` endpoint
#### GET params
- `slack_id`: Slack ID of whom you wanna check is an alt or not
#### Response (JSON)
- `is_alt` (bool): Is the user an alt?

- `verification_status` (`"needs_submission"` / `"pending"` / `"verified_eligible"` / `"verified_but_over_18"` / `"rejected"` / `"not_found"`): Refer to the [Hack Club Auth docs](https://auth.hackclub.com/docs/api#:~:text=Verification%20was%20rejected-,GET%20/api/external/check,-Check%20the%20verification)

- `is_verified` (bool): `true` if `verification_status` is either `verified_eligible` or `verified_but_over_18`

- `object` (object or null): has `created_at` (ISO 8601 extended), `parent_slack_id`, `id` (database id), and `child_slack_id` (same as `slack_id` query param). It is null when the user is not an alt.

#### Example
Request: `/check?slack_id=U0BQD70MNHL`

Response (pretty-printed):
```json
{
    "is_alt": true,
    "verification_status": "needs_submission",
    "is_verified": false,
    "object": {
        "id": 1,
        "created_at": "2026-10-03T13:54:20.990886Z",
        "parent_slack_id": "U0A7776A2MT",
        "child_slack_id": "U0BQD70MNHL"
    }
}
```

## Setup & Deployment

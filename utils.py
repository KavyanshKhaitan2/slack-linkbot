import random
import string
from typing import Literal

import requests

TOKEN_CHARS = string.ascii_uppercase + string.digits
HCA_BASE_URL = "https://auth.hackclub.com"

def generate_token(chars=6):
    return ''.join([random.choice(TOKEN_CHARS) for _ in range(chars)])

def check_verification_status(slack_user_id=None, email=None) -> Literal['needs_submission', 'pending', 'verified_eligible', 'verified_but_over_18', 'rejected', 'not_found']:
    if slack_user_id:
        r = requests.get(HCA_BASE_URL+f"/api/external/check?slack_id={slack_user_id}")
    else:
        r = requests.get(HCA_BASE_URL+f"/api/external/check?email={email}")
    r.raise_for_status()
    
    result = r.json()['result']

    return result

def is_verified(slack_user_id=None, email=None) -> bool:
    result = check_verification_status(slack_user_id=slack_user_id, email=email)
    return result in ["verified_eligible", "verified_but_over_18"]
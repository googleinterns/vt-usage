from models import *

import pytest


@pytest.mark.parametrize("api_key", ["\x00", "abc/abc", "abc'abc", "abc--abc"])
def test_email_wrapper_bad_api_key(api_key):
    try:
        APIKey(api_key=api_key)
    except ValueError:
        pass
 


@pytest.mark.parametrize("email", ["without.domain", "mail@withoutsufix", "mail@withoutsufix",
                                   "without.at.com", "strange@\x0char.com"])
def test_email_wrapper_bad_email(email):
    try:
        APIKeyEmail(api_key="abc123", email=email)
    except ValueError:
        pass


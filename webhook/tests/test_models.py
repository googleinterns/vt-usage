from models import *

import pytest


@pytest.mark.parametrize("api_key", ["123456789", "abcdefg", "abc123"])
def test_correct_api_key(api_key):
    assert APIKey(api_key=api_key).api_key == api_key


@pytest.mark.parametrize("api_key", ["\x00", "abc/abc", "abc'abc", "abc--abc"])
def test_bad_api_key(api_key):
    try:
        APIKey(api_key=api_key)
    except ValueError:
        return

    assert False


@pytest.mark.parametrize("email", ["good@email.com", "strange@domain.sufix", "with.dot@address.com",
                                   "with-dash@add.com", "with.two.dots@address.com"])
def test_api_key_email(email):
    assert APIKeyEmail(api_key="abc123", email=email).email == email


@pytest.mark.parametrize("email", ["without.domain", "mail@withoutsufix", "mail@withoutsufix",
                                   "without.at.com", "strange@\x0char.com"])
def test_api_key_email_bad_email(email):
    try:
        APIKeyEmail(api_key="abc123", email=email)
    except ValueError:
        return

    assert False

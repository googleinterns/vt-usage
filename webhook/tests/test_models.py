from models import *

import pytest


def test_email_wrapper_normal():
    api_key = "normalkey123123"
    email = "some.normal@email.address"
    obj = EmailWrapper(api_key=api_key, email=email)

    assert obj.api_key == api_key
    assert obj.email == email


@pytest.mark.parametrize("api_key", ["\x00", "abc/abc", "abc'abc", "abc--abc"])
def test_email_wrapper_bad_api_key(api_key):
    try:
        EmailWrapper(api_key=api_key, email="some@email.address")
    except ValueError:
        pass
    except:
        assert False


@pytest.mark.parametrize("email", ["without.domain", "mail@withoutsufix", "mail@withoutsufix",
                                   "without.at.com", "strange@\x0char.com"])
def test_email_wrapper_bad_email(email):
    try:
        EmailWrapper(api_key="abcd123", email=email)
    except ValueError:
        pass
    except:
        assert False

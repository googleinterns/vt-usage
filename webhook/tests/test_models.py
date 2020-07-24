from models import *


def test_email_wrapper_normal():
    api_key = "normalkey123123"
    email = "some.normal@email.address"
    obj = EmailWrapper(api_key=api_key, email=email)

    assert obj.api_key == api_key
    assert obj.email == email


def check_value_error(api_key="normalkey123123", email="some@email.address"):
    try:
        EmailWrapper(api_key=api_key, email=email)
    except ValueError:
        return True
    except:
        return False

def test_email_wrapper_bad_api_key():
    assert check_value_error(api_key="\x00")
    assert check_value_error(api_key="abc/abc")
    assert check_value_error(api_key="abc'abc")
    assert check_value_error(api_key="abc--abc")

def test_email_wrapper_bad_email():
    assert check_value_error(email="without.domain")
    assert check_value_error(email="mail@withoutsufix")
    assert check_value_error(email="many@at@domain.com")
    assert check_value_error(email="without.at.com")
    assert check_value_error(email="strange@\x0char.com")
    

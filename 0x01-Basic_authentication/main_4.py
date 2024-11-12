#!/usr/bin/env python3
""" Main 4 - Testing extract_user_credentials method
"""
from api.v1.auth.basic_auth import BasicAuth # type: ignore

a = BasicAuth()

print(a.extract_user_credentials(None))
print(a.extract_user_credentials(89))
print(a.extract_user_credentials("Holberton School"))
print(a.extract_user_credentials("Holberton:School"))
print(a.extract_user_credentials("bob@gmail.com:toto1234"))

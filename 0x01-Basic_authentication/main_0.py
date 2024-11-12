#!/usr/bin/env python3
""" Main 0  - Testing Auth class methods
"""
from api.v1.auth.auth import Auth # type: ignore

a = Auth()

print(a.require_auth("/api/v1/status/", ["/api/v1/status/"]))
print(a.authorization_header())
print(a.current_user())

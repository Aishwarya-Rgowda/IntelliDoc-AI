from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.routers.admin import require_admin


def test_admin_allowlist_denies_non_admin(monkeypatch):
    monkeypatch.setattr("app.routers.admin.ADMIN_EMAILS", {"admin@example.com"})
    user = SimpleNamespace(email="member@example.com")
    with pytest.raises(HTTPException) as exc:
        require_admin(user)
    assert exc.value.status_code == 403


def test_admin_allowlist_accepts_configured_admin(monkeypatch):
    monkeypatch.setattr("app.routers.admin.ADMIN_EMAILS", {"admin@example.com"})
    user = SimpleNamespace(email="ADMIN@example.com")
    assert require_admin(user) is user

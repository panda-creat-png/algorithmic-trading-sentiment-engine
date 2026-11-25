import logging
import secrets
import pytest
from pydantic import ValidationError
from app.core.config import Settings, MIN_SECRET_KEY_LENGTH


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)


def test_production_rejects_missing_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="")


def test_production_rejects_default_dev_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            SECRET_KEY="quantmind-ai-super-secret-development-jwt-key-replace-in-production",
        )


def test_production_rejects_short_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="short-key-123")


def test_production_accepts_strong_secret_key():
    strong_key = secrets.token_urlsafe(48)
    cfg = Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=strong_key)
    assert cfg.SECRET_KEY == strong_key
    assert len(cfg.SECRET_KEY) >= MIN_SECRET_KEY_LENGTH


def test_development_generates_ephemeral_secret_when_omitted(caplog):
    with caplog.at_level(logging.WARNING, logger="quantmind.config"):
        cfg1 = Settings(_env_file=None, ENVIRONMENT="development", SECRET_KEY="")
        cfg2 = Settings(_env_file=None, ENVIRONMENT="development", SECRET_KEY="")

    assert len(cfg1.SECRET_KEY) >= MIN_SECRET_KEY_LENGTH
    assert len(cfg2.SECRET_KEY) >= MIN_SECRET_KEY_LENGTH
    assert cfg1.SECRET_KEY != cfg2.SECRET_KEY
    assert "ephemeral random key" in caplog.text


def test_development_warns_on_weak_secret_but_allows_startup(caplog):
    dev_placeholder = "quantmind-ai-super-secret-development-jwt-key-replace-in-production"
    with caplog.at_level(logging.WARNING, logger="quantmind.config"):
        cfg = Settings(_env_file=None, ENVIRONMENT="development", SECRET_KEY=dev_placeholder)

    assert cfg.SECRET_KEY == dev_placeholder
    assert "Replace SECRET_KEY before deploying to production" in caplog.text

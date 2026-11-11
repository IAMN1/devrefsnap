import pytest
from pydantic import ValidationError

from demo_settings import Settings


def test_settings_environment_and_required_value(monkeypatch):
    monkeypatch.delenv("CHEATSHEET_PYDANTIC_DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    monkeypatch.setenv("CHEATSHEET_PYDANTIC_DATABASE_URL", "sqlite:///training.db")
    monkeypatch.setenv("CHEATSHEET_PYDANTIC_API_KEY", "training-key")
    settings = Settings(_env_file=None)
    assert settings.database_url == "sqlite:///training.db"
    assert settings.api_key.get_secret_value() == "training-key"
    assert "training-key" not in str(settings)

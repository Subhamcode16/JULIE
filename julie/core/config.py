"""Julie configuration loader."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class JulieConfig(BaseSettings):
    """Load config from .env and environment variables."""

    # LLM
    groq_api_key: str = ""
    cerebras_api_key: str = ""

    # Voice
    julie_wake_word: str = "hey julie"
    julie_voice: str = "en-US-AriaNeural"
    julie_log_level: str = "INFO"

    # Paths
    julie_data_dir: str = "./data"

    # Network
    julie_port_ws: int = 8765
    julie_port_http: int = 8766

    # Optional
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def db_path(self) -> Path:
        """SQLite database path."""
        p = Path(self.julie_data_dir)
        p.mkdir(exist_ok=True, parents=True)
        return p / "julie.db"

    @property
    def config_path(self) -> Path:
        """Config TOML path."""
        p = Path(self.julie_data_dir)
        p.mkdir(exist_ok=True, parents=True)
        return p / "config.toml"

    @property
    def blocked_paths_path(self) -> Path:
        """Blocked paths registry."""
        p = Path(self.julie_data_dir)
        p.mkdir(exist_ok=True, parents=True)
        return p / "blocked_paths.txt"

    def validate(self) -> bool:
        """Check required config is present."""
        if not self.groq_api_key and not self.cerebras_api_key:
            print("ERROR: No LLM API key set. Set GROQ_API_KEY or CEREBRAS_API_KEY in .env")
            return False
        return True


def load_config(validate_required: bool = False) -> JulieConfig:
    """Load and validate config."""
    config = JulieConfig()
    if validate_required:
        config.validate()
    return config


# Singleton
_config: JulieConfig | None = None


def get_config() -> JulieConfig:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config

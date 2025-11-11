from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class ExtractSettings(BaseSettings):
    file_url: str

    model_config = SettingsConfigDict(env_prefix="extract_")


class ExportSettings(BaseSettings):
    max_file_size_mb: int = 50
    file_name_prefix: Optional[str] = None
    folder_path: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="export_")


class MasterSettings(BaseSettings):
    debug: bool = False

    extract_settings: ExtractSettings = ExtractSettings()
    export_settings: ExportSettings = ExportSettings()

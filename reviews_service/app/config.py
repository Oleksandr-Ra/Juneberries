from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    reviews_mongo_username: str
    reviews_mongo_password: str
    reviews_mongo_host: str
    reviews_mongo_port: int
    reviews_mongo_db: str

    @property
    def reviews_mongo_url(self) -> str:
        return (
            f'mongodb://{self.reviews_mongo_username}:{self.reviews_mongo_password}'
            f'@{self.reviews_mongo_host}:{self.reviews_mongo_port}/{self.reviews_mongo_db}?authSource=admin'
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '../.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        extra='ignore'
    )
    api_v1_prefix: str = '/api/v1'
    db: DatabaseConfig


settings = Settings()

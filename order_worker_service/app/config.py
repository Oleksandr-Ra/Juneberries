from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseModel):
    broker: str
    order_create_topic: str
    order_update_topic: str


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int
    rate_exp: int  # minutes

    @property
    def redis_url(self) -> str:
        return f'redis://{self.host}:{self.port}/{self.db}'


class ExchangeAPIConfig(BaseModel):
    url: str
    key: str
    base_currency: str
    target_currency: str
    available_currency: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '../.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        extra='ignore'
    )

    kafka: KafkaConfig
    redis: RedisConfig
    exchange_api: ExchangeAPIConfig


settings = Settings()

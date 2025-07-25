from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthJWT(BaseModel):
    secret_key: str
    algorithm: str


class DatabaseConfig(BaseModel):
    catalog_pg_user: str
    catalog_pg_password: str
    catalog_pg_host: str
    catalog_pg_port: int
    catalog_pg_db: str

    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_N_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    }

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.catalog_pg_user,
            password=self.catalog_pg_password,
            host=self.catalog_pg_host,
            port=self.catalog_pg_port,
            path=self.catalog_pg_db,
        )


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int
    categories_ttl: int  # days


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '../.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        extra='ignore'
    )
    api_v1_prefix: str = '/api/v1'
    kafka_broker: str

    auth_jwt: AuthJWT
    db: DatabaseConfig
    redis: RedisConfig


settings = Settings()

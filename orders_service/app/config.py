from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    orders_pg_user: str
    orders_pg_password: str
    orders_pg_host: str
    orders_pg_port: int
    orders_pg_db: str

    echo: bool = False
    echo_pool: bool = False
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
    def orders_pg_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.orders_pg_user,
            password=self.orders_pg_password,
            host=self.orders_pg_host,
            port=self.orders_pg_port,
            path=f'/{self.orders_pg_db}',
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

from pydantic_settings import BaseSettings

class MySettings(BaseSettings):
    database_username: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str
    database_algorithm: str
    api_key: str
    database_minutes_expires_token: int

    class Config:
        env_file = ".env"

MySetting = MySettings()

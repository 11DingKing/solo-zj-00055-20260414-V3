import os


def strtobool(val: str) -> int:
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError(f"invalid truth value {val!r}")


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = bool(strtobool(os.getenv("FLASK_DEBUG", "false")))
    TESTING = False

    SERVER_NAME = os.getenv(
        "SERVER_NAME", "localhost:{0}".format(os.getenv("PORT", "8000"))
    )

    pg_user = os.getenv("POSTGRES_USER", "hello")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "password")
    pg_host = os.getenv("POSTGRES_HOST", "postgres")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB", pg_user)
    db = f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

    CELERY_CONFIG = {
        "worker_log_level": os.getenv("CELERY_LOG_LEVEL", "info"),
        "broker_url": REDIS_URL,
        "result_backend": REDIS_URL,
        "include": [],
    }


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


def get_config_class():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig


_current_config = get_config_class()

SECRET_KEY = _current_config.SECRET_KEY
DEBUG = _current_config.DEBUG
TESTING = _current_config.TESTING
SERVER_NAME = _current_config.SERVER_NAME
pg_user = _current_config.pg_user
pg_pass = _current_config.pg_pass
pg_host = _current_config.pg_host
pg_port = _current_config.pg_port
pg_db = _current_config.pg_db
db = _current_config.db
SQLALCHEMY_DATABASE_URI = _current_config.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = _current_config.SQLALCHEMY_TRACK_MODIFICATIONS
REDIS_URL = _current_config.REDIS_URL
CELERY_CONFIG = _current_config.CELERY_CONFIG

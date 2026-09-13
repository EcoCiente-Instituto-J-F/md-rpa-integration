from sqlalchemy import create_engine
from src.config.settings import settings



def create_source_engine():

    url = (
        f"postgresql://"
        f"{settings.SOURCE_USER}:"
        f"{settings.SOURCE_PASSWORD}@"
        f"{settings.SOURCE_HOST}:"
        f"{settings.SOURCE_PORT}/"
        f"{settings.SOURCE_DATABASE}"
    )


    return create_engine(url)



def create_target_engine():

    url = (
        f"postgresql://"
        f"{settings.TARGET_USER}:"
        f"{settings.TARGET_PASSWORD}@"
        f"{settings.TARGET_HOST}:"
        f"{settings.TARGET_PORT}/"
        f"{settings.TARGET_DATABASE}"
    )


    return create_engine(url)
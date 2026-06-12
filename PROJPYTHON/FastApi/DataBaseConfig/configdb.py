# from pydantic_settings import SettingsConfigDict,BaseSettings
# from typing import Optional
# from functools import lru_cache
#
# from pathlib import  Path
#
# envPath=Path(__file__).resolve().parent.parent
# envPath = envPath / ".env"
# class BasicConfig(BaseSettings):
#     ENV_STATE:Optional[str]=None
#     model_config = SettingsConfigDict(env_file=envPath,extra="ignore")
# class GlobalConfig(BasicConfig):
#     DATABASE_URL:Optional[str]=None
#     DB_FORCE_ROLL_BACK:bool=False
#
# class DevConfig(GlobalConfig):
#     model_config = SettingsConfigDict(env_prefix="DEV_",env_file=envPath,extra="ignore")
# @lru_cache()
# def get_Config(env_state:str):
#     configs={"dev":DevConfig}
#     return configs[env_state]()
# config = get_Config(BasicConfig().ENV_STATE)


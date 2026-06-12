from os import getenv

from redis import Redis
from dotenv import load_dotenv
load_dotenv()
password = getenv("REDIS_PASSWORD")
host = getenv("REDIS_HOST")

cache= Redis(
    host=host,
    port=11523,
    decode_responses=False,
    username="default",
    password=password,
)




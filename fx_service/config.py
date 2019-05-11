import environs
import pathlib
from loguru import logger

env = environs.Env()
basedir = pathlib.Path(__file__).parent
env_path = basedir.parent / ".env"
env.read_env(env_path.absolute(), recurse=False)

FORGE1_API_KEY = env.str("FORGE1_API_KEY")
DATABASE_URL = env.str("DATABASE_URL")

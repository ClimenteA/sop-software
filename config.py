from pydantic_settings import BaseSettings


DEVUSER = "admin"
DEVPASS = "secretpass"
DB = "DB"


class Config(BaseSettings):
    ADMIN_EMAIL: str = DEVUSER
    ADMIN_PASSWORD: str = DEVPASS
    ADMIN_USERNAME: str = DEVUSER
    STORAGE_PATH: str = "/home/storage"
    ALLOWED_ORIGINS: str = "*"
    DBLOCAL: bool = False
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "ERROR"
    LOG_RETENTION: str = "1 week"
    ME_CONFIG_BASICAUTH_PASSWORD: str = DEVPASS
    ME_CONFIG_BASICAUTH_USERNAME: str = DEVUSER
    ME_CONFIG_MONGODB_ADMINPASSWORD: str = DEVPASS
    ME_CONFIG_MONGODB_ADMINUSERNAME: str = DEVUSER
    ME_CONFIG_SITE_BASEURL: str = "/mongo-express"
    ME_CONFIG_SITE_COOKIESECRET: str = DEVPASS
    ME_CONFIG_SITE_SESSIONSECRET: str = DEVPASS
    MONGO_DATABASE: str = DB
    MONGO_EXPRESS_IMAGE_TAG: str = "0.54.0"
    MONGO_HOSTNAME: str = "mongo"
    MONGO_IMAGE_TAG: int = 5
    MONGO_INITDB_DATABASE: str = DB
    MONGO_INITDB_ROOT_PASSWORD: str = DEVPASS
    MONGO_INITDB_ROOT_USERNAME: str = DEVUSER
    MONGO_PORT: int = 27017
    PORT: int = 3000
    SECRET: str = DEVPASS
    DEMO_ACCOUNT: bool = False

    def get_mongo_uri(self):
        queryparams = "?authSource=admin&serverSelectionTimeoutMS=5000"
        if self.DBLOCAL:
            return f"mongodb://{self.ADMIN_USERNAME}:{self.ADMIN_PASSWORD}@localhost:{self.MONGO_PORT}/{self.MONGO_DATABASE}{queryparams}"
        return f"mongodb://{self.ADMIN_USERNAME}:{self.ADMIN_PASSWORD}@{self.MONGO_HOSTNAME}:{self.MONGO_PORT}/{self.MONGO_DATABASE}{queryparams}"


cfg = Config()

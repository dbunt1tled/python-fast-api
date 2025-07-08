from dependency_injector import containers, providers

from src.app.user.repository.user_repository import UserRepository
from src.app.user.service.user_service import UserService
from src.core.db.asmysql import MyDatabaseConfig
from src.core.service.hash import HashService
from src.core.settings.setting import Settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    cfg = providers.Singleton(Settings)
    db_config = providers.Singleton(
        MyDatabaseConfig,
        dsn=cfg.provided.sqlalchemy_database_uri
    )

    hash_service = providers.Singleton(
        HashService,
        jwt_public_key=cfg.provided.jwt_public_key,
        jwt_private_key=cfg.provided.jwt_private_key,
        jwt_algorithm=cfg.provided.jwt_algorithm,
        jwt_access_token_exp_h=cfg.provided.jwt_access_token_exp_h,
        jwt_refresh_token_exp_h=cfg.provided.jwt_refresh_token_exp_h,
    )
    user_repository = providers.Singleton(
        UserRepository,
        db_config=db_config,
    )
    user_service = providers.Singleton(
        UserService,
        user_repository=user_repository,
    )

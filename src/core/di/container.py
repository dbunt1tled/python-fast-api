from dependency_injector import containers, providers

from src.app.auth.service.auth_service import AuthService
from src.app.user.repository.user_repository import UserRepository
from src.app.user.service.user_service import UserService
from src.app.user_notification.repository.user_notification_repository import UserNotificationRepository
from src.app.user_notification.service.user_notification_service import UserNotificationService
from src.core.db.asmysql import MyDatabaseConfig
from src.core.service.email.app_mail_service import AppMailService
from src.core.service.email.email_service import EmailService
from src.core.service.email.view_service import ViewService
from src.core.service.hash import HashService
from src.core.settings.setting import Settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    cfg = providers.Singleton(Settings)
    db_config = providers.Singleton(
        MyDatabaseConfig,
        dsn=cfg.provided.sqlalchemy_database_uri
    )

    email_service = providers.Singleton(
        EmailService,
        smtp_server=cfg.provided.smtp_server,
        smtp_port=cfg.provided.smtp_port,
        app_password=cfg.provided.app_password,
        from_email=cfg.provided.from_email,
    )

    view_service = providers.Singleton(
        ViewService,
        template_dirs="src/core/service/email/templates",
        app_url=cfg.provided.app_url,
    )

    hash_service = providers.Singleton(
        HashService,
        cfg=cfg
    )

    app_email_service = providers.Singleton(
        AppMailService,
        email_service=email_service,
        view_service=view_service,
    )
    user_repository = providers.Singleton(
        UserRepository,
        db_config=db_config,
    )
    user_service = providers.Singleton(
        UserService,
        user_repository=user_repository,
    )

    user_notification_repository = providers.Singleton(
        UserNotificationRepository,
        db_config=db_config,
    )
    user_notification_service = providers.Singleton(
        UserNotificationService,
        user_notification_repository=user_notification_repository,
    )

    auth_service = providers.Singleton(
        AuthService,
        user_service=user_service,
        hash_service=hash_service,
        app_email_service=app_email_service,
    )


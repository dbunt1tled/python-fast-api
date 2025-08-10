from dependency_injector import containers, providers

from src.app.auth.service.auth_service import AuthService
from src.app.user.repository.user_repository import UserRepository
from src.app.user.service.user_service import UserService
from src.app.user_notification.repository.user_notification_repository import UserNotificationRepository
from src.app.user_notification.service.user_notification_service import UserNotificationService
from src.app.user_notification.service.ws_notification_service import WSNotificationService
from src.app.ws.service.ws_service import WSService
from src.core.db.asmysql import MyDatabaseConfig
from src.core.log.log import Log
from src.core.rabbit_mq.config import RabbitMQConfig
from src.core.rabbit_mq.consumer import AsyncRabbitMQConsumer
from src.core.rabbit_mq.producer import AsyncRabbitMQProducer
from src.core.rabbit_mq.rmq_service import RMQService
from src.core.service.email.app_mail_service import AppMailService
from src.core.service.email.email_service import EmailService
from src.core.service.email.view_service import ViewService
from src.core.service.hash_service import HashService
from src.core.settings.setting import Settings
from src.core.web_socket.ws_manager import WSManager


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    app_config = providers.Singleton(Settings)
    db_config = providers.Singleton(MyDatabaseConfig, dsn=app_config.provided.sqlalchemy_database_uri)

    log = providers.Singleton(
        Log,
        app_name=app_config().app_name,
        env=app_config().environment,
        service_name=app_config().service_name,
        loki_url=app_config().loki_url,
        loki_enabled=app_config().loki_enabled,
    )

    log_request = providers.Singleton(
        Log,
        app_name=app_config().app_name,
        env=app_config().environment,
        service_name="request",
        loki_url=app_config().loki_url,
        loki_enabled=app_config().loki_enabled,
    )

    log_rm = providers.Singleton(
        Log,
        app_name=app_config().app_name,
        env=app_config().environment,
        service_name="rabbitmq",
        loki_url=app_config().loki_url,
        loki_enabled=app_config().loki_enabled,
    )

    email_service = providers.Singleton(
        EmailService,
        smtp_server=app_config.provided.smtp_server,
        smtp_port=app_config.provided.smtp_port,
        app_password=app_config.provided.app_password,
        from_email=app_config.provided.from_email,
    )

    rmq_config = providers.Singleton(
        RabbitMQConfig,
        url=app_config.provided.rabbitmq_url,
    )

    rmq_producer = providers.Singleton(AsyncRabbitMQProducer, config=rmq_config, log=log_rm)
    rmq_consumer = providers.Singleton(AsyncRabbitMQConsumer, config=rmq_config, log=log_rm)
    rmq_service = providers.Singleton(
        RMQService,
        producer=rmq_producer,
    )

    view_service = providers.Singleton(
        ViewService,
        template_dirs="src/core/service/email/templates",
        app_url=app_config.provided.app_url,
    )

    hash_service = providers.Singleton(HashService, cfg=app_config)

    app_email_service = providers.Singleton(
        AppMailService,
        rmq_service=rmq_service,
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

    ws_manager = providers.Singleton(
        WSManager,
        log=log,
    )

    ws_notification_service = providers.Singleton(
        WSNotificationService,
        user_notification_service=user_notification_service,
        ws_manager=ws_manager,
        log=log,
    )

    ws_service = providers.Singleton(
        WSService,
        ws_manager=ws_manager,
        hash_service=hash_service,
        services=[ws_notification_service],
        log=log,
    )

    auth_service = providers.Singleton(
        AuthService,
        user_service=user_service,
        hash_service=hash_service,
        app_email_service=app_email_service,
    )

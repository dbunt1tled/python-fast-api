from src.app.user.data.role import Role
from src.app.user.data.user_status import UserStatus
from src.app.user.model.user import User
from src.app.user.service.user_service import UserService
from src.core.db.repository import Filter, Oper
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnauthorizedException, UnprocessableEntityException
from src.core.service.dto.token import TokenBearer, TokenType
from src.core.service.email.app_mail_service import AppMailService
from src.core.service.hash_service import HashService


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        hash_service: HashService,
        app_email_service: AppMailService,
    ) -> None:
        self.user_service = user_service
        self.hash_service = hash_service
        self.app_email_service = app_email_service

    async def login(self, email: str, password: str) -> TokenBearer:
        user = await self.user_service.one(
            filters=[
                Filter("email", Oper.EQ, email),
            ]
        )
        if user is None:
            raise UnauthorizedException(error_no=ErrorNo.USER_EMAIL_NOT_FOUND, message="Unauthorized!")
        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException(error_no=ErrorNo.USER_STATUS_NOT_ACTIVE, message="Unauthorized!")

        if not self.hash_service.verify_password(password=password, hashed_password=user.hash_password):
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_USER_PASSWORD_INVALID, message="Unauthorized!")
        user = await self.user_service.update(uid=user.id, data={"session": self.hash_service.random_string()})

        return self.hash_service.create_token_bearer(user=user)

    async def signup(
        self,
        first_name: str,
        second_name: str,
        email: str,
        password: str,
    ) -> User:
        user = await self.user_service.one(
            filters=[
                Filter("email", Oper.EQ, email),
            ]
        )
        if user is not None:
            raise UnprocessableEntityException(
                error_no=ErrorNo.USER_EMAIL_ALREADY_EXISTS, message="User already exists"
            )

        user = User(
            first_name=first_name,
            second_name=second_name,
            email=email,
            hash_password=self.hash_service.hash_password(password),
            session=self.hash_service.random_string(),
            status=UserStatus.PENDING,
            roles=[Role.USER],
        )
        user = await self.user_service.create(data=user)
        await self.send_confirm_email(user)
        return user

    async def send_confirm_email(self, user: User) -> None:
        if user.status != UserStatus.PENDING:
            return

        token = self.hash_service.create_token_confirm(user=user)
        await self.app_email_service.send_confirm_email(user=user, token=token)

    async def confirm_user(self, jwt: str) -> None:
        token = self.hash_service.verify_token(token=jwt)
        if token is None:
            raise UnprocessableEntityException(
                error_no=ErrorNo.CONFIRM_TOKEN_INVALID, message="Confirmation token is invalid"
            )

        if token.token_type != TokenType.CONFIRMATION:
            raise UnprocessableEntityException(
                error_no=ErrorNo.CONFIRM_TOKEN_TYPE_WRONG, message="Confirmation token is invalid"
            )
        user = await self.user_service.one(
            filters=[
                Filter("email", Oper.EQ, token.email),
            ]
        )
        if user is None:
            raise UnprocessableEntityException(
                error_no=ErrorNo.CONFIRM_TOKEN_USER_NOT_FOUND, message="Confirmation token is invalid"
            )
        if user.session != token.session:
            raise UnprocessableEntityException(
                error_no=ErrorNo.CONFIRM_TOKEN_USER_SESSION_INVALID, message="Confirmation token is invalid"
            )
        await self.user_service.update(uid=user.id, data={"status": UserStatus.ACTIVE})

    async def refresh(self, jwt: str) -> TokenBearer:
        token = self.hash_service.verify_token(token=jwt)
        if token is None:
            raise UnauthorizedException(error_no=ErrorNo.REFRESH_TOKEN_INVALID, message="Unauthorized!")
        if token.token_type != TokenType.REFRESH:
            raise UnauthorizedException(error_no=ErrorNo.REFRESH_TOKEN_TYPE_INVALID, message="Unauthorized!")

        user = await self.user_service.get_by_id(uid=int(token.subject))
        if user is None:
            raise UnauthorizedException(error_no=ErrorNo.REFRESH_TOKEN_USER_NOT_FOUND, message="Unauthorized!")
        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException(error_no=ErrorNo.REFRESH_TOKEN_USER_STATUS_NOT_ACTIVE, message="Unauthorized!")

        if user.session != token.session:
            raise UnauthorizedException(error_no=ErrorNo.REFRESH_TOKEN_USER_SESSION_INVALID, message="Unauthorized!")

        user = await self.user_service.update(uid=user.id, data={"session": self.hash_service.random_string()})

        return self.hash_service.create_token_bearer(user=user)

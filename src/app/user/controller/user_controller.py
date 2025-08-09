from fastapi import APIRouter, Depends, FastAPI, Request

from src.app.user.dto.user import UserCreateRequest, UserListRequest
from src.core.db.repository import Filter, FilterOperator, Pagination
from src.core.di.container import Container
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnprocessableEntityException
from src.core.http.controller import BaseController
from src.core.http.response.response import JsonApiResponse


class UserController(BaseController):
    def __init__(self, app: FastAPI, container: Container) -> None:
        super().__init__(container=container)
        router = APIRouter(prefix="/users", tags=["users"])
        router.add_api_route(path="", endpoint=self.list, methods=["GET"])
        router.add_api_route(path="", endpoint=self.create, methods=["POST"])
        router.add_api_route(path="/{user_id}", endpoint=self.view, methods=["GET"])
        app.include_router(router=router)

    async def list(self, req: UserListRequest = Depends()) -> JsonApiResponse:
        users = await self.container.user_service().all(
            filters=[
                Filter("email", FilterOperator.EQ, req.email),
            ],
            pagination=Pagination(
                per_page=req.per_page or 10,
                page=req.page or 1,
            ),
        )

        return await self.response(data=users, include=req.include)

    async def view(self, user_id: int, req: Request) -> JsonApiResponse:
        user = await self.container.user_service().get_by_id(user_id)
        return await self.response(data=user, include=req.query_params.get("include", None))

    async def create(
        self,
        req: UserCreateRequest,
    ) -> JsonApiResponse:
        user = await self.container.user_service().one(
            filters=[
                Filter("email", FilterOperator.EQ, req.email),
            ]
        )
        if user is not None:
            raise UnprocessableEntityException(
                error_no=ErrorNo.USER_EMAIL_ALREADY_EXISTS, message="User already exists"
            )

        user = req.to_user()
        user.session = self.container.hash_service().random_string()
        user.hash_password = self.container.hash_service().hash_password(req.password)
        user = await self.container.user_service().create(data=user)

        return await self.response(data=user)

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class DTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        alias_generator=AliasGenerator(
            alias=to_camel,
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    include: str | None = None


class Message(DTO):
    message: str


class Paginated(DTO):
    page: int | None = None
    per_page: int | None = None
    order_field: str | None = None
    order_by: str | None = None

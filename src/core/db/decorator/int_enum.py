from sqlalchemy import Integer, TypeDecorator

class IntEnum(TypeDecorator):
    impl = Integer
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs) -> None:
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value if isinstance(value, self.enum_class) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class(value)
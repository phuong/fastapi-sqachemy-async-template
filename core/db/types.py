import uuid

from sqlalchemy.types import String, TypeDecorator


class UUID(TypeDecorator):
    """
    sqlalchemy UUID field
    """

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if not isinstance(value, uuid.UUID):
            try:
                return uuid.UUID(value).hex
            except (ValueError, AttributeError):
                return None
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


default_uuid = uuid.uuid4

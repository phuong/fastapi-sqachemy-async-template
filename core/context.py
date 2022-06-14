import copy
from typing import Any, Dict, NoReturn, Optional, cast

from _contextvars import ContextVar, Token, copy_context

from core.config import Language


_context: ContextVar[Any] = ContextVar("_request_context", default={})


class _Context:
    def __setattr__(self, key: str, value: Any) -> NoReturn:
        _context.get()[key] = value

    @property
    def data(self) -> Dict[str, Any]:
        """
        Dump this to json. Object itself it not serializable.
        """
        try:
            return cast(Dict[str, Any], _context.get())
        except LookupError as ex:
            raise RuntimeError("Please add ContextMiddle to use this feature") from ex

    @staticmethod
    def exists() -> bool:
        return _context in copy_context()

    def copy(self) -> Dict[str, Any]:
        """
        Read only context data.
        """
        return copy.copy(self.data)

    @staticmethod
    def init(data: Dict[str, Any] = {}) -> Token:
        return _context.set(data)

    @staticmethod
    def get(key: str) -> Optional[Any]:
        return _context.get().get(key, None)

    @staticmethod
    def set(key: str, value: Any) -> NoReturn:
        _context.get()[key] = value

    @staticmethod
    def reset(token: Token) -> NoReturn:
        _context.reset(token)

    @property
    def language(self) -> Language:
        return _context.get().get("language", Language.English)


request_context = _Context()

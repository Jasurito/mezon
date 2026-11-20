"""Перевод ключей сценария и служебных сообщений."""

from app.i18n.messages import message
from app.i18n.translate import fallback_chain, translate

__all__ = ["fallback_chain", "message", "translate"]

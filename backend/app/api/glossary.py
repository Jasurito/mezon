from fastapi import APIRouter
from pydantic import BaseModel

from app.i18n.glossary import get_glossary
from app.schemas.legal import Locale

router = APIRouter(tags=["reference"])


class GlossaryTerm(BaseModel):
    id: str
    term: str
    definition: str
    aliases: list[str]  # словоформы для подсветки термина в тексте


@router.get("/glossary", response_model=list[GlossaryTerm])
def glossary(locale: Locale = "ru"):
    """Словарик терминов с простыми определениями."""
    return get_glossary(locale)

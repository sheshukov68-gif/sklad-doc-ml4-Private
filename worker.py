"""Воркфлоу sklad-doc-ml4: извлечение позиций из складских документов через Mistral Large 4."""

import asyncio
import json

from pydantic import BaseModel

import mistralai_workflows
import mistralai_workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client

MODEL = "mistral-large-latest"

SCHEMA_HINT = """
{
  "items": [
    {
      "name": "наименование позиции",
      "article": "артикул/марка или null",
      "quantity": 0,
      "unit": "шт|кг|м|м2|м3|компл",
      "movement": "приход|расход",
      "counterparty": "контрагент/основание или null",
      "comment": "примечание или null"
    }
  ]
}
"""


class DocInput(BaseModel):
    """Вход воркфлоу: текст документа и его тип."""

    document_text: str
    document_type: str = "накладная"


@workflows.activity()
async def extract_items(
    document_text: str,
    document_type: str,
    client=Depends(get_mistral_client),
) -> dict:
    """Извлекает позиции документа в структуру для складского журнала."""
    prompt = (
        "Ты — обработчик складских документов. Тип документа: "
        + document_type
        + ". Извлеки из текста все позиции (материалы, изделия, крепёж). "
        "Верни СТРОГО JSON-объект по схеме:\n"
        + SCHEMA_HINT
        + "\nЕсли тип движения не указан, считай его 'приход'. Текст документа:\n"
        + document_text
    )
    response = await client.chat.complete_async(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except (TypeError, ValueError):
        return {"items": [], "parse_error": True, "raw": str(content)[:2000]}
    items = data.get("items", [])
    return {"items": items, "parse_error": False}


@workflows.workflow.define(
    name="sklad-doc-ml4",
    workflow_display_name="Складские документы → позиции (ML4)",
    workflow_description="Извлекает позиции из накладных и спецификаций через Mistral Large 4 и готовит строки для складского журнала.",
)
class SkladDocWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: DocInput) -> dict:
        extraction = await extract_items(input.document_text, input.document_type)
        items = extraction.get("items", [])

        prihod = [i for i in items if i.get("movement") == "приход"]
        rashod = [i for i in items if i.get("movement") == "расход"]
        summary = (
            "Документ: " + input.document_type
            + ". Позиций: " + str(len(items))
            + ". Приход: " + str(len(prihod))
            + ", расход: " + str(len(rashod)) + "."
        )
        return {
            "document_type": input.document_type,
            "items": items,
            "counts": {"total": len(items), "prihod": len(prihod), "rashod": len(rashod)},
            "summary": summary,
            "parse_error": extraction.get("parse_error", False),
        }


async def main():
    await mistralai_workflows.run_worker([SkladDocWorkflow])


if __name__ == "__main__":
    asyncio.run(main())

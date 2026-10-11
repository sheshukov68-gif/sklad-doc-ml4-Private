# sklad-doc-ml4

Воркфлоу **sklad-doc-ml4**: извлечение позиций из накладных и спецификаций через Mistral Large 4.

## Self-hosted запуск

```bash
git clone https://github.com/sheshukov68-gif/sklad-doc-ml4-Private.git
cd sklad-doc-ml4-Private
uv sync
MISTRAL_API_KEY=<ключ> DEPLOYMENT_NAME=sklad-doc-ml4 uv run python worker.py
```

Windows PowerShell:

```powershell
git clone https://github.com/sheshukov68-gif/sklad-doc-ml4-Private.git
cd sklad-doc-ml4-Private
uv sync
$env:MISTRAL_API_KEY="<ключ>"
$env:DEPLOYMENT_NAME="sklad-doc-ml4"
uv run python worker.py
```

Воркер зарегистрирует воркфлоу `sklad-doc-ml4` в воркспейсе — запускать из Studio или API:
POST https://api.mistral.ai/v1/workflows/sklad-doc-ml4/execute

## Вход

```json
{"document_text": "текст накладной", "document_type": "накладная"}
```

## Выход

items (наименование, артикул, количество, единица, приход/расход, контрагент, примечание), counts, summary.

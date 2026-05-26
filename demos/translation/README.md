# MbazaNLP Translation Demonstrator

English ↔ Kinyarwanda machine translation using MbazaNLP's fine-tuned NLLB-200 models.

## Models

Three domain-adapted models are available on HuggingFace:

| Domain | Model ID | Use case |
|--------|----------|----------|
| General | [`mbazaNLP/Nllb_finetuned_general_en_kin`](https://huggingface.co/mbazaNLP/Nllb_finetuned_general_en_kin) | Everyday text, mixed domains |
| Education | [`mbazaNLP/Nllb_finetuned_education_en_kin`](https://huggingface.co/mbazaNLP/Nllb_finetuned_education_en_kin) | Academic and instructional content |
| Tourism | [`mbazaNLP/Nllb_finetuned_tourism_en_kin`](https://huggingface.co/mbazaNLP/Nllb_finetuned_tourism_en_kin) | Travel and hospitality content |

All models are licensed under **Apache 2.0**.

## Requirements

- Python 3.9+
- ~3 GB disk space per model (downloaded automatically on first use)
- GPU optional — CPU inference works but is slower

## Installation

```bash
pip install -r requirements.txt
```

## CLI usage

```bash
# English → Kinyarwanda (general domain)
python translate.py "Hello, how are you?"

# Kinyarwanda → English
python translate.py "Muraho, amakuru?" --src kin_Latn --tgt eng_Latn

# Use the education model
python translate.py "The student passed the exam." --domain education

# Use the tourism model
python translate.py "Book a room near the national park." --domain tourism
```

**Language codes:**

| Language | Code |
|----------|------|
| English | `eng_Latn` |
| Kinyarwanda | `kin_Latn` |

**Domain options:** `general` (default) · `education` · `tourism`

## Notebook

Open `translation_demo.ipynb` in Jupyter for an interactive walkthrough covering:

- English → Kinyarwanda and Kinyarwanda → English
- Domain comparison (same sentence across all three models)
- Batch translation
- Interactive translation cell

```bash
pip install jupyter
jupyter notebook translation_demo.ipynb
```

## Notes on domain selection

Use the **general** model when the text does not clearly belong to a specific domain, or when translating mixed content.

Use **education** for instructional text, curriculum materials, academic writing, or anything involving students, teachers, and learning objectives.

Use **tourism** for travel content, hotel and restaurant descriptions, cultural guides, and visitor-facing communications.

Domain-adapted models consistently outperform the general model on in-domain sentences. The difference is most visible with technical vocabulary and domain-specific phrasing.

## About MbazaNLP

MbazaNLP is an open-source community building NLP tools for Kinyarwanda and East African languages.

- Website: [aimbaza.org](https://aimbaza.org)
- All models: [huggingface.co/mbazaNLP](https://huggingface.co/mbazaNLP)
- GitHub: [github.com/MBAZA-NLP](https://github.com/MBAZA-NLP)
- Slack: [aimbaza.slack.com](https://aimbaza.slack.com)

To report issues or contribute improvements to this demo, open an issue on GitHub or post in `#models` on Slack.

"""
MbazaNLP Translation Demo
English <-> Kinyarwanda using fine-tuned NLLB-200 models.

Usage:
    python translate.py "Hello, how are you?"
    python translate.py "Muraho, amakuru?" --src kin_Latn --tgt eng_Latn
    python translate.py "The student passed the exam." --domain education
    python translate.py "Book a hotel near the national park." --domain tourism
"""

import argparse
import sys


MODELS = {
    "general": "mbazaNLP/Nllb_finetuned_general_en_kin",
    "education": "mbazaNLP/Nllb_finetuned_education_en_kin",
    "tourism": "mbazaNLP/Nllb_finetuned_tourism_en_kin",
}

LANG_LABELS = {
    "eng_Latn": "English",
    "kin_Latn": "Kinyarwanda",
}


def translate(text, src_lang="eng_Latn", tgt_lang="kin_Latn", domain="general"):
    from transformers import pipeline

    model_id = MODELS[domain]
    print(f"Loading {domain} model ({model_id})...", file=sys.stderr)

    translator = pipeline(
        "translation",
        model=model_id,
        src_lang=src_lang,
        tgt_lang=tgt_lang,
    )
    result = translator(text, max_length=512)
    return result[0]["translation_text"]


def main():
    parser = argparse.ArgumentParser(
        description="Translate between English and Kinyarwanda using MbazaNLP models."
    )
    parser.add_argument("text", help="Text to translate")
    parser.add_argument(
        "--src",
        default="eng_Latn",
        choices=list(LANG_LABELS),
        metavar="LANG",
        help="Source language code (default: eng_Latn). Options: eng_Latn, kin_Latn",
    )
    parser.add_argument(
        "--tgt",
        default="kin_Latn",
        choices=list(LANG_LABELS),
        metavar="LANG",
        help="Target language code (default: kin_Latn). Options: eng_Latn, kin_Latn",
    )
    parser.add_argument(
        "--domain",
        default="general",
        choices=list(MODELS),
        help="Translation domain: general, education, or tourism (default: general)",
    )
    args = parser.parse_args()

    if args.src == args.tgt:
        parser.error("Source and target language must be different.")

    result = translate(args.text, src_lang=args.src, tgt_lang=args.tgt, domain=args.domain)

    src_label = LANG_LABELS[args.src]
    tgt_label = LANG_LABELS[args.tgt]
    print(f"\n[{src_label}] {args.text}")
    print(f"[{tgt_label}] {result}")


if __name__ == "__main__":
    main()

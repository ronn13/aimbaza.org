from django.shortcuts import render

HF = "https://huggingface.co/mbazaNLP"
HF_DS = "https://huggingface.co/datasets/mbazaNLP"

TRANSLATION_MODELS = [
    {
        "name": "NLLB Fine-tuned — General (En↔Kin)",
        "desc": "NLLB-200 1.3B fine-tuned on general-purpose English–Kinyarwanda data.",
        "url": f"{HF}/Nllb_finetuned_general_en_kin",
    },
    {
        "name": "NLLB Fine-tuned — Education (En↔Kin)",
        "desc": "NLLB-200 1.3B fine-tuned on education-domain data (Coursera, Atingi).",
        "url": f"{HF}/Nllb_finetuned_education_en_kin",
    },
    {
        "name": "NLLB Fine-tuned — Tourism (En↔Kin)",
        "desc": "NLLB-200 1.3B fine-tuned on tourism-domain English–Kinyarwanda data.",
        "url": f"{HF}/Nllb_finetuned_tourism_en_kin",
    },
    {
        "name": "NLLB Education (full card)",
        "desc": "Education-domain translation model with complete model card.",
        "url": f"{HF}/NLLB-Education",
    },
    {
        "name": "NLLB Tourism 8-bit Quantized",
        "desc": "Tourism translation model quantized to 8-bit for CPU inference.",
        "url": f"{HF}/Nllb_finetuned_tourism_8bit",
    },
    {
        "name": "Quantized NLLB — Education 8-bit",
        "desc": "Education translation model quantized to 8-bit via CTranslate2.",
        "url": f"{HF}/Quantized_Nllb_Finetuned_Edu_En_Kin_8bit",
    },
    {
        "name": "Quantized NLLB — Tourism 8-bit",
        "desc": "Tourism translation model quantized to 8-bit via CTranslate2.",
        "url": f"{HF}/Quantized_Nllb_Finetuned_Tourism_En_Kin_8bit",
    },
]

ASR_MODELS = [
    {
        "name": "Kinyarwanda Coqui STT",
        "desc": "Coqui STT model for Kinyarwanda automatic speech recognition.",
        "url": f"{HF}/kinyarwanda-coqui-stt-model",
    },
    {
        "name": "Kinyarwanda NeMo Conformer",
        "desc": "NeMo Conformer-CTC-Large ASR fine-tuned on Kinyarwanda speech.",
        "url": f"{HF}/Kinyarwanda_nemo_stt_conformer_model",
    },
    {
        "name": "Whisper Small — Kinyarwanda",
        "desc": "OpenAI Whisper-small fine-tuned on Common Voice Kinyarwanda.",
        "url": f"{HF}/Whisper-Small-Kinyarwanda",
    },
    {
        "name": "Multilingual ASR (Rw / Sw / Lg)",
        "desc": "NeMo Conformer-CTC-Large for Kinyarwanda, Swahili, and Luganda.",
        "url": f"{HF}/stt_rw_sw_lg_conformer_ctc_large",
    },
]

OTHER_MODELS = [
    {
        "name": "Kinyarwanda TTS",
        "desc": "Text-to-Speech model producing natural Kinyarwanda speech.",
        "url": f"{HF}/kinyarwanda-tts-model",
    },
    {
        "name": "Bakame Chatbot",
        "desc": "Rasa-based Kinyarwanda chatbot. Gated — request access on model page.",
        "url": f"{HF}/bakame-chatbot-kinyarwanda",
    },
]

DATASETS = [
    {
        "name": "NMT Education Parallel Corpus (En–Kin)",
        "desc": (
            "61,767 sentence pairs for education-domain English–Kinyarwanda"
            " translation (Coursera, Atingi, Wikipedia)."
        ),
        "url": f"{HF_DS}/NMT_Education_parallel_data_en_kin",
    },
    {
        "name": "PIQA-kin",
        "desc": "Physical commonsense reasoning benchmark in Kinyarwanda (binary QA).",
        "url": f"{HF_DS}/PIQA-kin",
    },
]


def index(request):
    return render(
        request,
        "projects/projects.html",
        {
            "translation_models": TRANSLATION_MODELS,
            "asr_models": ASR_MODELS,
            "other_models": OTHER_MODELS,
            "datasets": DATASETS,
        },
    )

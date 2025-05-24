SYSTEM_EXTRACT_MEDICAL = """
A partir do texto abaixo de uma consulta médica, extraia e organize as informações no seguinte formato JSON:
{{
    "queixa_principal": "...",
    "historia_doenca_atual": "...",
    "antecedentes": "...",
    "exame_fisico": "...",
    "hipotese_diagnostica": "...",
    "conduta": "...",
    "prescricao": "...",
    "encaminhamentos": "..."
}}

Texto:
\"\"\"
{transcription_text}
\"\"\"
Retorne apenas o JSON.
"""

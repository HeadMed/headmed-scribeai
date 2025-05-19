from groq import Groq
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = Groq()



def extract_structured_info(transcription_text: str) -> dict:
    prompt = f"""
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

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw_content = response.choices[0].message.content
    print("LLM RAW RESPONSE:", raw_content)

    try:
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if not json_match:
            raise ValueError("JSON não encontrado na resposta do modelo.")
        json_str = json_match.group()
        return json.loads(json_str)
    except Exception as e:
        print("Erro ao fazer parse do JSON:", e)
        print("Conteúdo bruto da resposta:", raw_content)
        raise

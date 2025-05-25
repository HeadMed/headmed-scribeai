import re
import json

def extract_json_from_text(text):
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError('JSON not founded on text')
        json_str = json_match.group()
        return json.loads(json_str)
    except Exception as e:
        print(f'Error on JSON parsing: {e}')
        raise
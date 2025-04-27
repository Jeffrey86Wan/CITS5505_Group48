import openai
import os
import re
import demjson3

def send_to_chatgpt(prompt):
    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    raw_chunk = response.choices[0].message.content.strip()

    # Save raw GPT output
    with open("raw_chatgpt_response.txt", "w", encoding="utf-8") as f:
        f.write(raw_chunk)

    # Clean top and bottom junk
    first_bracket = raw_chunk.find('[')
    last_bracket = raw_chunk.rfind(']')
    if first_bracket != -1 and last_bracket != -1:
        raw_chunk = raw_chunk[first_bracket:last_bracket+1]

    raw_chunk = raw_chunk.replace("“", '"').replace("”", '"')
    raw_chunk = raw_chunk.replace("‘", "'").replace("’", "'").replace("`", "'")
    raw_chunk = re.sub(
        r'("amount"\s*:\s*")(\d{1,3}(,\d{3})+(\.\d+)?)(")',
        lambda m: f'{m.group(1)}{m.group(2).replace(",", "")}{m.group(5)}',
        raw_chunk
    )

    expenses_chunk = demjson3.decode(raw_chunk)

    for item in expenses_chunk:
        if 'direct debit' in item['description'].lower() or (item.get('amount') and float(item['amount']) < 0):
            item['type'] = 'credit'
        else:
            item['type'] = 'debit'

    return expenses_chunk

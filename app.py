# 3. Call OpenAI (Responses API)
try:
    resp = requests.post(
        'https://api.openai.com/v1/responses',
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            # 你可以先用 gpt-4o / gpt-4.1 / gpt-5（看你帳號可用哪些）
            'model': 'gpt-4o',
            'instructions': system,
            'input': messages,   # 直接沿用你組好的 messages
            'max_output_tokens': 1500,
        },
        timeout=30
    )
    result = resp.json()

    # 把 output 裡的文字抽出來（兼容不同回傳形態）
    answer_parts = []
    for item in result.get('output', []):
        if item.get('type') == 'message' and item.get('role') == 'assistant':
            for c in item.get('content', []):
                # 常見是 {"type":"output_text","text":"..."}
                if isinstance(c, dict) and 'text' in c:
                    answer_parts.append(c['text'])
    answer = "\n".join(answer_parts).strip() or "（AI 沒有回傳文字）"

    return jsonify({'answer': answer})
except Exception as e:
    return jsonify({'error': str(e)}), 500

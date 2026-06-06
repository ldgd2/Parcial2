import asyncio
from openai import AsyncOpenAI

async def test_ia():
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="sk-or-v1-XXXXXXXXXX",
    )
    user_content = [
        {"type": "text", "text": "Hola, devuelve { \"status\": \"ok\" }"}
    ]
    
    try:
        response = await client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[
                {"role": "user", "content": user_content},
            ],
            timeout=20
        )
        print("Success:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Error:")
        print(e)

asyncio.run(test_ia())

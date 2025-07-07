from openai import OpenAI


system_prompt = "You are in a crypto-related group chat of other people in discord. Come up with a unique greeting. keep track of all responses you have given already. make sure each one is unique. it should be short as well. Just answer to this prompt with a greeting and thats it. also make sure you dont send the response in quotes. Do not use emojis"
advanced_base_prompt = "Imagine you are in a crypto-related chat with other people in discord. There are a lot of anonymous people talking about fun things: sports, hobbies, music, and so on. Start the conversation or join up to an existing one. The starting message may or may not come next. Answer just like people do. As a reply to a message, not to a prompt. Make sure you dont send the response in quotes. DO NOT USE EMOJIS. One last thing: the messages in chat should be short and precise, informal style, slang is ok, because nobody writes there formally and longer than 10-15 words"


def ask_chatgpt(
    api_key: str, message: str | None = None, advanced_chat: bool = False
) -> str:
    client = OpenAI(api_key=api_key)

    messages = []
    if not advanced_chat:
        messages.append({"role": "system", "content": system_prompt})
    else:
        messages.append({"role": "system", "content": advanced_base_prompt})
        if message:
            messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error occurred: {str(e)}"

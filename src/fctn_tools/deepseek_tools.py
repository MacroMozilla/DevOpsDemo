import os
from typing import List, Dict
from openai import OpenAI

from utility.watch import Watch

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


def get_response_once(response):
    return response.choices[0].message.content.strip()


def get_response_stream(response):
    for chunk in response:
        if chunk.choices[0].delta.content:  # 过滤掉空的 delta
            for char in chunk.choices[0].delta.content:
                yield char


def call_deepseek(msgs: List[Dict], model="deepseek-chat", stream=True):
    """
    调用 OpenAI API 进行对话，返回模型回答。
    """
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")  # 从环境变量获取 API 密钥

    try:
        response = client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=0.7,
            stream=stream
        )

        if stream:
            return get_response_stream(response)
        else:
            return get_response_once(response)

    except Exception as e:
        return f"调用 API 出错: {e}"


# 示例调用
if __name__ == "__main__":
    pass
    stream = True
    model = "deepseek-chat"

    user_input = "introduce yourself"
    msgs = [{"role": "user", "content": user_input}]

    print(f"model = {model}, stream = {stream}")
    print(f"{'=' * 25} [start] {'=' * 25}")
    length = 0
    w = Watch()

    if not stream:
        result = call_deepseek(msgs, model=model, stream=stream)
        print(result)
        length = len(result)
    else:
        gen_answer = call_deepseek(msgs, model=model, stream=stream)

        buffer = []
        for chunk in gen_answer:
            buffer.append(chunk)
            print(chunk, end="", flush=True)
        length = len(buffer)

    cost = w.see_seconds()
    print()
    print(f"{'=' * 25} [end] [stream={stream}] {'=' * 25}")

    print(f"total cost:{cost}")
    print(f"cost per char:{cost / length}")

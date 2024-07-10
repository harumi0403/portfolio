import os
import base64
from openai import OpenAI


# 画像をbase64にエンコードする関数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 画像のパス
image_path = "/Users/harumiuduki/Documents/img_1.jpg"

# 画像をbase64にエンコードする
base64_image = encode_image(image_path)

# OpenAI APIのクライアントを作成する.
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# チャットの応答を生成する
response = client.chat.completions.create(
    model="gpt-4o", # "gpt-4-turbo-2024-04-09",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "画像から文字を読み取ってください。"},
                {"type": "image_url","image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"}}
            ],
        }
    ],
    max_tokens=300,
)

# 応答を表示する
print(response.choices[0])

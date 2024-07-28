import os
import glob
import base64
import pandas as pd
from collections import defaultdict
from openai import OpenAI


def encode_image(image_path : str) -> str:
    """画像を読み込みOpen AI APIで扱える文字列に変換する

    Args:
        image_path (str): 撮影した画像のパス
    
    Returns:
        str: 画像をbase64形式に変換した文字列
    """

    # 画像を読み込みOpen AI APIで扱える文字列に変換する
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_response(image_path : str) -> str:
    """画像とプロンプトをOpen AI APIに送信し、レスポンスを取得する

    Args:
        image_path (str): 撮影した画像のパス
    
    Returns:
        str: レスポンス
    """

    # 画像をbase64にエンコードする
    base64_image = encode_image(image_path)

    # OpenAI APIのクライアントを作成する.
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # チャットの応答を生成する
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "user",
            # NOTE: プロンプトの内容はダミーデータ
            "content": [
                {"type": "text", "text": "画像から文字を読み取り,を区切り文字に1行で出力してください。" + \
                "回答例　NO：5, 氏名：佐藤浩一, 性別：男, 生年月日：1988.04.20, 住所：大阪府大阪市北区大深町1-1, " + \
                "電話番号：06-0000-5678, 携帯番号：080-8765-4321, メールアドレス：kouichi.satou@gmail.com, " + \
                "日にち：2020.07.08, 詳細：Rx 126331, 金額：¥2118600"},
                {"type": "image_url","image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"}}
            ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content

def parse_response(response : str) -> dict:
    """レスポンスをパースしお客様カードのデータを取得する

    Args:
        response (str): Open AI APIによるお客様カードの読み取り結果
    
    Returns:
        dict: お客様カードのデータを格納した辞書
    """

    # データを格納する辞書を初期化する
    data_dict = dict(NO="", 氏名="", 性別="", 生年月日="", 住所="", 電話番号="",  携帯番号="",  メールアドレス="", \
                     日にち="", 詳細="", 金額="")

    # 文字列をカンマで分割する
    response = response.split(",")

    # 各データごとに繰り返す
    for data in response:
        # 文字列をセミコロンで分割する
        key   = data.split("：")[0].strip() 
        value = data.split("：")[1].strip()
    
        # 辞書にデータを格納する
        if key in data_dict.keys():
            data_dict[key] = value

    return data_dict

def main():
    """お客様カードの内容を読み取りcsvとして保存する
    """
        
    # お客様カードのパスを取得する
    image_paths = sorted(glob.glob("./img/お客様カード_*.jpg"))
    print("お客様カード:", image_paths)

    # 各画像について処理を行う
    data_list = list()
    for image_path in image_paths:
        # Open AI APIを使ってお客様カードの文字を読み取る
        response  = get_response(image_path)

        # レスポンスをパースする
        data_dict = parse_response(response)
        data_list.append(data_dict)

        print("読み取り完了:", image_path)

    # お客様カードのデータを1つの辞書にマージする
    result_dict = defaultdict(list)
    for data_dict in data_list:
        for key, value in data_dict.items():
            result_dict[key].append(value)
    print("読み取り結果:", result_dict)

    # マージした辞書をcsvに保存する
    df = pd.DataFrame(result_dict, index=[no for no in result_dict["NO"]])
    df.to_csv("result.csv", index=False)

if __name__ == "__main__":
    main()

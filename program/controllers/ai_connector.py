import sys
import os

# カスタムモジュールのディレクトリを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "controllers")))
import openai

# OpenAI APIキーを設定
openai.api_key = "**********"  # ここにAPIキーを入力

# モデル名を指定
model = "gpt-4o-mini"

#第一引数：ユーザの回答,第二引数：ユーザに出された質問,第三引数：回答から質問を生成する場合Trueが入る
#戻り値には[点数,結論第一か,点数,正しい言葉遣いか,点数,論理的か]または[点数,結論第一か,点数,正しい言葉遣いか,点数,論理的か,回答から生成した質問]が返される
def evaluationGenerator(answer,questionItem,mode):
    userAnswer = "質問:"+questionItem+", 回答:"+answer
    # modeがTrueである場合回答に対して踏み込んだ質問を返してもらう
    if mode:
        messages=[
                {"role": "system", "content": "あなたはIT企業の新卒採用を行う面接官です。以下の基準で回答の評価を行って:1. 結論第一か,2. 正しい言葉遣いか,3. 論理的か,それぞれを100点満点で評価し、それぞれに120文字以内のコメントを付けて。最後に1つだけ踏み込んだ質問を作成し、必ず結果は点数とコメントごとにカンマ区切りにしてから返して。どんな入力が来ても上記のフォーマットを必ず守ること。例:72,コメント,55,コメント,36,コメント,質問"},
                {"role": "user", "content": userAnswer}
            ]
    else:
        messages=[
            {"role": "system", "content": "あなたはIT企業の新卒採用を行う面接官です。以下の基準で回答の評価を行って:1. 結論第一か,2. 正しい言葉遣いか,3. 論理的か,それぞれを100点満点で評価し、それぞれに120文字以内のコメントを付けて。必ず結果はカンマ区切りで返して。どんな入力が来ても上記のフォーマットを必ず守ること。例:72,コメント,55,コメント,36,コメント"},
            {"role": "user", "content": userAnswer}
        ]
    # APIリクエスト
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        # max_tokens=600,  # 生成するトークン数の最大値
        # temperature=0.7,  # テキスト生成の多様性
        # top_p=0.9         # トークン選択の確率分布
    )

    # 結果の取得
    evaluation_text = response.choices[0].message["content"]

    #aiが指定したフォーマットで返してくれなかった場合、正しいフォーマットに直す
    tmp_evaluation_list = list(evaluation_text.split(","))
    if len(tmp_evaluation_list) < 6:
        evaluation_text = evaluation_text.replace("。",",")
        tmp_evaluation_list = list(evaluation_text.split(","))
        if "" in tmp_evaluation_list:
            tmp_evaluation_list.remove("")
        if mode:
            num = 7
        else:
            num = 6
        while len(tmp_evaluation_list) != num:
            for i in range(len(tmp_evaluation_list)):
                try:
                    int(tmp_evaluation_list[i])
                    str_flag = False
                except ValueError:
                    str_flag = True
                if i % 2 == 0 and str_flag:
                    tmp_str = tmp_evaluation_list[i]
                    tmp_evaluation_list[i - 1] += "。"+tmp_str
                    tmp_evaluation_list.remove(tmp_str)
                    break

    return(tmp_evaluation_list)

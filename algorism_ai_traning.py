import os
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from random import choice

# .env の読み込み
load_dotenv()

# 環境変数
endpoint    = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment  = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_key     = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# バリデーション
if not all([endpoint, deployment, api_key, api_version]):
    st.error("環境変数が正しく設定されていません。")
    st.stop()

# AzureOpenAI クライアント
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version,
)

st.set_page_config(page_title="アルゴリズム思考トレーニングAI", layout="wide")
st.title("🧠 アルゴリズム思考トレーニングAI")

# システムメッセージ
system_message = {
    "role": "system",
    "content": (
        "あなたは開発入門者の論理的思考を育成する教育アシスタントです\n"
        "ユーザーが提示した問題とアルゴリズムのステップに対して\n"
        "1.構成の素晴らしさや不足を指摘\n"
        "2.最適化や利便さの要素を含む代替案\n"
        "3.思考を深める質問を提示\n"
        "を旨としたコメントを日常的な例えも使いながら行ってください"
    )
}

# サンプル
sample_problems = [
    "リストから最も頻繁に出現する要素を求める",
    "配列から最大値を求める",
    "回文かどうかを判定する",
    "同じ値が連続するものを削除する"
]

# チャットAPI

def call_chat(messages, **kwargs):
    return client.chat.completions.create(
        model=deployment,
        messages=messages,
        **kwargs
    )

# タブ
tab1, tab2 = st.tabs(["1. 問題と思考を入力", "2. AIからフィードバック"])

with tab1:
    st.header("1. 問題とアルゴリズム思考を入力")

    # 問題モード選択
    problem_mode = st.radio("問題の選択方法", ["サンプルから選択", "AIがランダムに生成"], horizontal=True)

    # session_state 初期化
    if "ai_generated_problem" not in st.session_state:
        st.session_state.ai_generated_problem = ""
    if "selected_sample_problem" not in st.session_state:
        st.session_state.selected_sample_problem = ""
    if "custom_problem" not in st.session_state:
        st.session_state.custom_problem = ""

    # 問題入力欄
    target_problem = ""
    user_created_problem = False
    if problem_mode == "サンプルから選択":
        selected_index = 0
        if st.session_state.selected_sample_problem in sample_problems:
            selected_index = sample_problems.index(st.session_state.selected_sample_problem) + 1

        selected = st.selectbox(
            "サンプル問題を選択",
            [""] + sample_problems,
            index=selected_index,
            key="sample_select"
        )
        st.session_state.selected_sample_problem = selected

        st.session_state.custom_problem = st.text_input(
            "自分で問題を入力 (例: データを昇順に並び替える)",
            value=st.session_state.custom_problem,
            key="custom_input"
        )
        if st.session_state.custom_problem:
            target_problem = st.session_state.custom_problem
            user_created_problem = True
        else:
            target_problem = st.session_state.selected_sample_problem
    else:
        if st.button("ランダム問題を生成する", key="generate_random"):
            user_msg = {
                "role": "user",
                "content": (
                    "開発入門者向けに、多種多様なアルゴリズム学習用の問題タイトルを「リストから最も頻繁に出現する要素を求める」のような形で1件だけ生成してください。追加でコメントやレビューなどは不要です。過去に出たような典型問題（最大値・最頻値・ソートなど）を避け、工夫や発想が求められるテーマにしてください。"
                )
            }
            with st.spinner("AIが問題を考え中..."):
                res = call_chat(messages=[system_message, user_msg], max_tokens=200, temperature=0.7)
                st.session_state.ai_generated_problem = res.choices[0].message.content.strip().strip('"')
        st.text_input("AI生成問題タイトル", value=st.session_state.ai_generated_problem, key="ai_generated_display", disabled=True)
        target_problem = st.session_state.ai_generated_problem

    # ステップ入力
    st.subheader("ステップ (実装手順)")
    steps = st.text_area("アルゴリズムの日本語や擬似コードで入力",
                         placeholder="（入力例）一時リストを作成してカウントを計算...")

    # 思考理由入力
    st.subheader("その思考の理由")
    reason = st.text_area("なぜその順序や方法で考えたかを説明",
                         placeholder="（入力例）リストを作成して計算することで...")

    # フィードバック生成
    if st.button("フィードバックを受け取る", key="get_feedback"):
        if not (target_problem and steps and reason):
            st.warning("全て入力してください")
        else:
            comment_note = "" if user_created_problem else "問題に対するコメントは省略してください。"
            user_msg = {
                "role": "user",
                "content": (
                    f"問題: {target_problem}\n"
                    f"思考ステップ: {steps}\n"
                    f"考えた理由: {reason}\n"
                    f"{comment_note}\n"
                    "上記情報をもとに、アルゴリズムの構成を検証し、\n"
                    "1.良い点と改善点\n2.代替案やヒント\n3.思考を深める質問\nを教えてください"
                )
            }
            with st.spinner("生成中..."):
                res = call_chat(messages=[system_message, user_msg], max_tokens=800, temperature=0.6)
            st.session_state.feedback = res.choices[0].message.content



with tab2:
    st.header("2. フィードバック結果")
    st.markdown(st.session_state.get("feedback", "まだフィードバックはありません"))

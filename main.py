import streamlit as st
from dotenv import load_dotenv
from ai_utils import call_chat
from prompts import system_message, generate_three_methods_prompt, generate_followup_prompt

# .env の読み込み
load_dotenv()

# ページ設定
st.set_page_config(page_title="問題解決サポートAI bot", layout="wide")
st.title("問題解決サポートAI bot")

# ------------------------------------------------------------
# セッションステートの初期化
# ------------------------------------------------------------
if "user_problem" not in st.session_state:
    st.session_state.user_problem = ""
if "methods" not in st.session_state:
    st.session_state.methods = []              # 手法A, B, C をまとめて格納するリスト
if "selected_method_index" not in st.session_state:
    st.session_state.selected_method_index = None
if "followup_response" not in st.session_state:
    st.session_state.followup_response = ""

# ------------------------------------------------------------
# ステップ1：ユーザーが「解決したい問題」を入力
# ------------------------------------------------------------
st.header("1. 解決したい問題を入力してください")
user_input = st.text_area(
    "例：毎日更新される CSV から重複を除去してデータベースへ登録したい",
    value=st.session_state.user_problem,
    height=100
)
st.session_state.user_problem = user_input

# ------------------------------------------------------------
# 「３つの解法を生成」ボタン
# ------------------------------------------------------------
generate_btn = st.button("３つの解法を生成する", key="gen_methods_btn")
if generate_btn:
    if not st.session_state.user_problem.strip():
        st.warning("まずは解決したい問題を入力してください。")
    else:
        # クリアしてから再生成する
        st.session_state.methods = []

        with st.spinner("AI が３つの解決手段を生成中..."):
            # 1回の API 呼び出しで手法A/B/C が一度に返ってくるよう指示する
            messages = [
                system_message,
                generate_three_methods_prompt(st.session_state.user_problem)
            ]
            res = call_chat(messages=messages, max_tokens=1000, temperature=0.7)
            ai_content = res.choices[0].message.content.strip()

        parts = []
        # "2. 手法B:" の前までを parts[0] とする
        if "2. 手法B:" in ai_content:
            idx_b = ai_content.index("2. 手法B:")
            parts.append(ai_content[:idx_b].strip())
            remainder = ai_content[idx_b:].strip()
        else:
            # 安全策：もし見つからなかったら全文を parts[0] に
            parts.append(ai_content)
            remainder = ""

        # "3. 手法C:" の前までを parts[1] とする
        if remainder and "3. 手法C:" in remainder:
            idx_c = remainder.index("3. 手法C:")
            parts.append(remainder[:idx_c].strip())
            parts.append(remainder[idx_c:].strip())
        else:
            # 見つからなければ、残りすべてを parts[1] としておき、
            # parts[2] は空にしておく
            if remainder:
                parts.append(remainder)
            parts.append("")

        # parts の長さを 3 になるように調整（足りない場合は空文字を詰める）
        while len(parts) < 3:
            parts.append("")

        # 最終的に session_state に格納
        st.session_state.methods = parts


# ------------------------------------------------------------
# ステップ2の表示：方法A, 方法B, 方法C をそれぞれ個別のセクションで表示
# ------------------------------------------------------------
if st.session_state.methods:
    st.markdown("---")
    st.header("2. AIが提案した３つのアプローチ")

    for idx, method_text in enumerate(st.session_state.methods):
        label = "ABC"[idx]
        title = f"方法{label}"
        with st.expander(title):
            # 空文字の場合は「まだ生成されていません」と出す例
            if method_text:
                st.markdown(method_text.replace("\n", "  \n"))
            else:
                st.markdown("_（手法が生成されていないか、分割がうまくいきませんでした）_")

    # ------------------------------------------------------------
    # ステップ3：ユーザーに「どの方法を採用するか」を選択させる
    # ------------------------------------------------------------
    st.markdown("---")
    st.subheader("3. 実装したいアプローチを選択してください")
    options = []
    for idx, method_text in enumerate(st.session_state.methods):
        # method_text が空なら「生成なし」と表示
        if method_text:
            first_line = method_text.split("\n")[0].strip()
        else:
            first_line = "（手法が生成されていません）"
        label = "ABC"[idx]
        options.append(f"{first_line}")

    choice = st.radio(
        label="▼ 方法を選択",
        options=options,
        index=0 if st.session_state.selected_method_index is None else st.session_state.selected_method_index,
        key="method_choice"
    )
    selected_idx = options.index(choice)
    st.session_state.selected_method_index = selected_idx

    followup_btn = st.button("選択した手法で詳細フォローを受け取る", key="followup_btn")
    if followup_btn:
        if st.session_state.selected_method_index is None:
            st.warning("まずはアプローチを選択してください。")
        else:
            selected_method_text = st.session_state.methods[st.session_state.selected_method_index]
            with st.spinner("AI が詳細フォローを生成中..."):
                messages = [
                    system_message,
                    generate_followup_prompt(
                        st.session_state.user_problem,
                        selected_method_text
                    )
                ]
                res2 = call_chat(messages=messages, max_tokens=1000, temperature=0.7)
                st.session_state.followup_response = res2.choices[0].message.content.strip()


# ------------------------------------------------------------
# ステップ4の表示：フォロー結果を表示
# ------------------------------------------------------------
if st.session_state.followup_response:
    st.markdown("---")
    st.header("4. 選択した手法に対する詳細フォロー")
    st.markdown(st.session_state.followup_response.replace("\n", "  \n"))

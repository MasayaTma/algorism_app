# main.py

import os
import streamlit as st
from dotenv import load_dotenv

from ai_utils import call_chat
from prompts import system_message, generate_three_methods_prompt, generate_followup_prompt

# .env の読み込み
load_dotenv()

# ページ設定
st.set_page_config(page_title="開発フォローAIbot", layout="wide")
st.title("問題解決サポートAI bot")

# ------------------------------------------------------------
# セッションステートの初期化
# ------------------------------------------------------------
if "user_problem" not in st.session_state:
    st.session_state.user_problem = ""
if "methods" not in st.session_state:
    st.session_state.methods = []              # 手法A, B, C を格納するリスト
if "selected_method_index" not in st.session_state:
    st.session_state.selected_method_index = None
if "followup_response" not in st.session_state:
    st.session_state.followup_response = ""

# 各手法の「追加チャット履歴」を保持する辞書
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {0: [], 1: [], 2: []}

# ============================================================
# 1. 解決したい問題を入力＆３手法生成（セクション）
# ============================================================
with st.expander("1. 解決したい問題を入力＆３手法生成", expanded=True):
    st.write("以下のテキストエリアに「解決したい問題」を入力し、「３つの解法を生成する」ボタンを押してください。")
    user_input = st.text_area(
        "例：毎日更新される CSV から重複を除去してデータベースに登録したい",
        value=st.session_state.user_problem,
        height=100
    )
    st.session_state.user_problem = user_input

    if st.button("３つの解法を生成する", key="gen_methods_btn"):
        if not st.session_state.user_problem.strip():
            st.warning("まずは解決したい問題を入力してください。")
        else:
            # 既存データをクリア
            st.session_state.methods = []
            st.session_state.selected_method_index = None
            st.session_state.followup_response = ""
            for idx in range(3):
                st.session_state.chat_histories[idx] = []

            with st.spinner("AI が３つの解決手段を生成中..."):
                messages = [
                    system_message,
                    generate_three_methods_prompt(st.session_state.user_problem)
                ]
                res = call_chat(messages=messages, max_tokens=1000, temperature=0.7)
                ai_content = res.choices[0].message.content.strip()

            # 「1. 手法A:」「2. 手法B:」「3. 手法C:」で分割
            parts = []
            if "2. 手法B:" in ai_content:
                idx_b = ai_content.index("2. 手法B:")
                parts.append(ai_content[:idx_b].strip())
                remainder = ai_content[idx_b:].strip()
            else:
                parts.append(ai_content)
                remainder = ""

            if remainder and "3. 手法C:" in remainder:
                idx_c = remainder.index("3. 手法C:")
                parts.append(remainder[:idx_c].strip())
                parts.append(remainder[idx_c:].strip())
            else:
                if remainder:
                    parts.append(remainder)
                parts.append("")

            while len(parts) < 3:
                parts.append("")

            st.session_state.methods = parts
            st.success("３つの手法が生成されました。次のセクションを開いてご確認ください。")

    # 生成済みの手法があればプレビューだけ表示
    if st.session_state.methods:
        st.markdown("---")
        st.subheader("※ 生成済みの手法の見出しプレビュー")
        for idx, method_text in enumerate(st.session_state.methods):
            label = "ABC"[idx]
            if method_text:
                first_line = method_text.split("\n", 1)[0].strip()
            else:
                first_line = "(生成なし)"
            st.write(f"{first_line}")

# ============================================================
# 2. ３つのアプローチ表示（セクション）
# ============================================================
with st.expander("2. AIが提案した３つのアプローチ", expanded=False):
    if not st.session_state.methods:
        st.info("まずは上の「1. 解決したい問題を入力＆３手法生成」で手法を生成してください。")
    else:
        st.markdown("以下が AI が提案した３つのアプローチです。タイトルをクリックすると詳細が表示されます。")
        for idx, method_text in enumerate(st.session_state.methods):
            label = "ABC"[idx]
            # フラットに見出し＋内容を表示（expander をネストしない）
            st.markdown(f"#### 手法{label}")
            if method_text:
                st.markdown(method_text.replace("\n", "  \n"))
            else:
                st.markdown("_（未生成または分割に失敗しました）_")
            st.markdown("---")

# ============================================================
# 3. 手法選択＆詳細フォロー（セクション）
# ============================================================
with st.expander("3. 手法選択＆詳細フォロー", expanded=False):
    if not st.session_state.methods:
        st.info("まずは「1. 解決したい問題を入力＆３手法生成」で手法を生成してください。")
    else:
        st.write("実装したいアプローチを選択して、「詳細フォローを受け取る」を押してください。")
        # 手法選択用ラジオボタン
        options = []
        for idx, method_text in enumerate(st.session_state.methods):
            if method_text:
                first_line = method_text.split("\n", 1)[0].strip()
            else:
                first_line = "（生成なし）"
            options.append(first_line)

        choice = st.radio(
            label="▼ 手法を選択",
            options=options,
            index=0 if st.session_state.selected_method_index is None else st.session_state.selected_method_index,
            key="method_choice"
        )
        st.session_state.selected_method_index = options.index(choice)

        if st.button("選択した手法で詳細フォローを受け取る", key="followup_btn"):
            sel_idx = st.session_state.selected_method_index
            sel_method_text = st.session_state.methods[sel_idx]
            with st.spinner("AI が詳細フォローを生成中..."):
                messages = [
                    system_message,
                    generate_followup_prompt(st.session_state.user_problem, sel_method_text)
                ]
                res2 = call_chat(messages=messages, max_tokens=2000, temperature=0.7)
                st.session_state.followup_response = res2.choices[0].message.content.strip()

                # 詳細フォローをチャット履歴の初回応答として追加
                st.session_state.chat_histories[sel_idx].append({
                    "role": "assistant",
                    "content": st.session_state.followup_response
                })

        # 詳細フォローの表示
        if st.session_state.followup_response:
            st.markdown("---")
            st.subheader("選択した手法に対する詳細フォロー")
            st.markdown(st.session_state.followup_response.replace("\n", "  \n"))

# ============================================================
# タブ：4. 追加チャット＆過去チャット履歴
# ============================================================
tab_main, tab_history = st.tabs(["4. 追加チャット", "過去チャット履歴"])

# ------ タブ「4. 追加チャット」 ------
with tab_main:
    sel_idx = st.session_state.selected_method_index
    if sel_idx is None:
        st.info("まずは「3. 手法選択＆詳細フォロー」で手法を選び、詳細フォローを取得してください。")
    else:
        st.subheader(f"現在の選択： 手法{'ABC'[sel_idx]}")

        with st.form(key="chat_form"):
            user_chat = st.text_input(
                "追加で質問や補足を入力してください",
                placeholder="ここに入力して「送信」すると自動でクリアされます"
            )
            submit = st.form_submit_button(label="送信")

            if submit:
                if user_chat.strip():
                    # ユーザー発言を履歴に追加
                    st.session_state.chat_histories[sel_idx].append({
                        "role": "user",
                        "content": user_chat
                    })

                    # AI に投げるメッセージを構築
                    messages = [system_message]
                    selected_method_text = st.session_state.methods[sel_idx]
                    messages.append({
                        "role": "system",
                        "content": (
                            "以下はユーザーが選択した手法の説明です。\n\n" +
                            selected_method_text
                        )
                    })
                    # 過去のやり取りをすべて追加
                    for msg in st.session_state.chat_histories[sel_idx]:
                        messages.append(msg)
                    # 今回のユーザー発言を追加
                    messages.append({
                        "role": "user",
                        "content": user_chat
                    })

                    # AI 呼び出し
                    with st.spinner("AI が応答を生成中..."):
                        res3 = call_chat(messages=messages, max_tokens=1500, temperature=0.7)
                        ai_reply = res3.choices[0].message.content.strip()

                    # AI 応答を履歴に追加
                    st.session_state.chat_histories[sel_idx].append({
                        "role": "assistant",
                        "content": ai_reply
                    })
                else:
                    st.warning("質問内容を入力してください。")

        # フォーム送信後に、改めて履歴を表示
        history = st.session_state.chat_histories[sel_idx]
        if history:
            st.markdown("---")
            st.subheader("最新のやり取り（クリックして詳細を確認）")
            for i, msg in enumerate(history):
                if msg["role"] == "assistant":
                    content = msg["content"].replace(chr(10), "  \n")
                    st.markdown("**AI の応答 #{}:**  {}".format(i + 1, content))
                else:
                    st.markdown("**You の発言 #{}:**  {}".format(i + 1, msg["content"]))

# ------ タブ「過去チャット履歴」 ------
with tab_history:
    sel_idx = st.session_state.selected_method_index
    if sel_idx is None:
        st.info("まだ表示できる過去チャットはありません。まずは「4. 追加チャット」でやり取りをしてください。")
    else:
        st.subheader(f"手法{'ABC'[sel_idx]} の過去チャット履歴一覧")
        history = st.session_state.chat_histories[sel_idx]

        if not history:
            st.write("_まだチャットがありません。4. 追加チャットで質問してください。_")
        else:
            # 各過去メッセージを独立したセクション（expander 相当）で表示
            for i, msg in enumerate(history):
                preview = msg["content"].split("\n", 1)[0]
                title = f"{'AI' if msg['role']=='assistant' else 'You'} の発言 #{i+1}: {preview}"
                with st.expander(title):
                    st.markdown(msg["content"].replace(chr(10), "  \n"))

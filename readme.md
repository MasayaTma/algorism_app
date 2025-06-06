# 🧠 アルゴリズム思考トレーニングAI（３メソッド版）

開発入門者向けに、**ひとつの問題を入力すると AI が３つの解決手段を提案し、その中から選んだ方法をさらに詳しくフォローする**トレーニングアプリです。Streamlit 上で「問題」→「３手法提案」→「手法選択」→「詳細サポート」という流れをシームレスに体験できます。

---

## 🚀 主な特徴

1. **問題を入力すると AI が３つの手法を自動提案**  
   - 与えられた問題（例：「CSV から重複を除去して DB に登録したい」）に対し、  
     - 手法A：ツール／プラットフォームを使ったアプローチ  
     - 手法B：別のツール／手法  
     - 手法C：さらに異なる手法  
     の３つを番号付きで提示します（「ツール名／実装手順／必要ライブラリ／メリット・デメリット」を含む）。

2. **提案された３つの手法を折りたたみ式で表示**  
   - Streamlit の `st.expander` によって、手法A・B・C をそれぞれ見出し付きで展開できます。  
   - 初学者でも「まずタイトルだけを見る」「詳細を開いてステップを確認する」という使い方がしやすい UI。

3. **実装したい手法を選択 → 詳細サポートを取得**  
   - ３つの手法それぞれの「タイトル行」をプルダウン（`st.radio`）で選択可能。  
   - 選択後に「選択した手法で詳細フォローを受け取る」ボタンを押すと、  
     その手法に特化した「ステップバイステップの実装手順」「注意点」「擬似コード・サンプルコード」「よくあるつまずきポイント」を AI が返してくれます。

4. **セッションステートによる履歴保持**  
   - 各回の「問題入力」「３手法提案」「詳細フォロー」結果を `st.session_state` に保持。  
   - ページをリロードしても過去の結果を見返せるので、自分の成長を振り返りやすい。

---

## 🛠️ 使用技術

- **Python 3.8+**  
- **Streamlit** … UI フレームワーク  
- **Azure OpenAI API（ChatGPT/GPT-4）** … 対話型 AI エンジン  
- **`openai`（Python SDK）** … Azure OpenAI 連携  
- **python-dotenv** … `.env` による環境変数管理  

---

## 📦 セットアップ手順

1. **リポジトリをクローン**  
   ```bash
   git clone https://github.com/MasayaTma/algorism_app.git
   cd algorism_app
   ```

2. **仮想環境を作成して有効化**  
   - macOS / Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     python -m venv venv
     venv\Scripts\activate.bat
     ```

3. **依存パッケージをインストール**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   `requirements.txt` には以下が含まれています:
   ```
   streamlit
   openai
   python-dotenv
   ```

4. **`.env` ファイルを作成・設定**  
   プロジェクトルートに `.env` を置き、以下を記述します：
   ```
   AZURE_OPENAI_ENDPOINT=https://<YourResourceName>.openai.azure.com/
   AZURE_OPENAI_API_KEY=<YourAzureOpenAIKey>
   AZURE_OPENAI_API_VERSION=<YourApiVersion>      # 例: 2023-03-15-preview
   AZURE_OPENAI_DEPLOYMENT=<YourDeploymentName>    # 例: gpt-35-turbo
   ```
   - `AZURE_OPENAI_ENDPOINT`：Azure OpenAI リソースのエンドポイント  
   - `AZURE_OPENAI_API_KEY`：Azure OpenAI の API キー  
   - `AZURE_OPENAI_API_VERSION`：API バージョン文字列  
   - `AZURE_OPENAI_DEPLOYMENT`：デプロイ済みモデル名  

---

## 🎯 使い方ガイド

1. **アプリ起動**  
   ```bash
   streamlit run main.py
   ```
   ブラウザで `http://localhost:8501` にアクセスします。

2. **問題を入力**  
   - 画面上部のテキストエリアに「どんな問題を解きたいか」を自然文で入力します。  
   - 例：`毎日更新される CSV ファイルから特定の列を抽出し、重複を除去してデータベースに保存したい`

3. **「３つの解法を生成する」ボタンを押す**  
   - AI が 1 回だけ呼び出され、与えられた問題に対して３つの手法をまとめて返します。  
   - 各手法には「ツール名」「実装手順」「必要ライブラリ例」「メリット・デメリット」を含む番号付きフォーマットで出力されます。

4. **３つの手法を折りたたみ式で確認**  
   - 「手法A」「手法B」「手法C」のエクスパンダーを開いて、それぞれの詳細を確認します。  
   - 各手法の最初の行がタイトル行になっているので、どの手法を選びたいかイメージしやすいです。

5. **実装したい手法を選択**  
   - 「ステップ3」で `st.radio` によって「手法A:＜タイトル＞」「手法B:＜タイトル＞」「手法C:＜タイトル＞」という選択肢が表示されます。  
   - 自分が挑戦したいと感じた手法のラジオボタンを選びます。

6. **「選択した手法で詳細フォローを受け取る」ボタンを押す**  
   - 選択された手法テキスト（タイトル＋説明）を再度 AI に渡し、「この手法を実装するときの具体的なステップ／注意点／コード例／つまずきやすいポイント」を詳しく出力してもらえます。  
   - その結果が画面下部に表示され、学習者は実装サンプルをそのまま試せます。

7. **履歴を振り返る**  
   - 画面をスクロールするか、再度ページをリロードしても、以前に生成された「３つの手法」「詳細フォロー」は `session_state` に保存されているため消えません。  
   - 過去の回答を見返すことで、自分の思考の変化や理解度を追跡できます。

---

## 💡 サンプル画面イメージ

1. **問題入力画面**  
   ```
   1. 解決したい問題を入力してください
   [ テキストエリア: 毎日更新される CSV ファイルから重複を除去して
     データベースに登録したい ]
   [３つの解法を生成する] ボタン
   ```

2. **３つの手法提案（折りたたみ式）**  
   ```
   2. AIが提案した３つのアプローチ
   ┌─ 手法A [v]
   │  → Python スクリプトで pandas を使う方法
   │    - a) ツール名: Python + pandas + SQLAlchemy
   │    - b) 実装手順: 1. CSV 読み込み 2. drop_duplicates() 3. DB 保存
   │    - c) 必要ライブラリ: pandas, sqlalchemy
   │    - d) メリット: 大量データ対応可、スケジュール実行可能
   │    - e) デメリット: 環境構築が必要、コーディング学習が必要
   └─────────────────────────────
   ┌─ 手法B [v]
   │  → Excel の「重複の削除」機能と VBA マクロを使う方法
   │    - a) ツール名: Excel + VBA
   │    ...
   └─────────────────────────────
   ┌─ 手法C [v]
   │  → Power Automate で自動化フローを組む方法
   │    - a) ツール名: Power Automate (クラウドフロー)
   │    ...
   └─────────────────────────────
   ```

3. **手法選択 & 詳細フォロー**  
   ```
   3. 実装したいアプローチを選択してください
   (*) 手法A: Python スクリプトで pandas
       手法B: Excel マクロ
       手法C: Power Automate

   [選択した手法で詳細フォローを受け取る] ボタン
   ```

4. **詳細フォロー表示**  
   ```
   4. 選択した手法に対する詳細フォロー
   → Python スクリプト（pandas）での具体的なコード例
     1. pandas で CSV 読み込む
     2. DataFrame.drop_duplicates() を使う
     3. SQLAlchemy で DB に INSERT
     ... 
   ```

---

## 📂 ファイル構成例

```
algorism_app/
├─ main.py                # Streamlit メインアプリ
├─ ai_utils.py            # Azure OpenAI 呼び出しラッパー関数
├─ prompts.py             # generate_three_methods_prompt / generate_followup_prompt
├─ requirements.txt       # 必要パッケージ一覧
├─ .env.example           # 環境変数のサンプル (.env にリネームして使用)
└─ README.md              # 本ドキュメント
```

- **main.py**：UI ロジック、Streamlit ウィジェット、AI 呼び出しのフロー  
- **ai_utils.py**：`call_chat` 関数で Azure OpenAI API をラップ  
- **prompts.py**：  
  - `generate_three_methods_prompt(user_problem)`  
  - `generate_followup_prompt(user_problem, selected_method)`  
- **.env.example**：環境変数テンプレート（実際には `.env` にコピー）  
- **requirements.txt**：以下のように最低限必要です  
  ```
  streamlit
  openai
  python-dotenv
  ```

---

## 🤝 貢献・修正（Pull Request）歓迎

1. このリポジトリを Fork する  
2. 新しいブランチを作成 (`git checkout -b feature/xxx`)  
3. 変更をコミット (`git commit -m "add: 新機能の説明"`)  
4. リモートにプッシュ (`git push origin feature/xxx`)  
5. GitHub 上で Pull Request を作成し、変更内容を簡潔に説明してください

---

## 📜 ライセンス

本プロジェクトは MIT ライセンス のもとで公開されています。  

---

### 最後に

「問題を入力 → AI が３つ提案 → 手法を選択 → 詳細フォロー」のサイクルを繰り返すことで、自分のアルゴリズム思考や実装力を効率的に向上させましょう。何かご不明点や要望があれば Issue や Discussions でお気軽にご連絡ください！🚀

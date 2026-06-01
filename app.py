import streamlit as st
import pandas as pdimport streamlit as st
import pandas as pd
import itertools
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="チームナビ Pro (AI搭載)", page_icon="🧭", layout="wide")

# カスタムCSS（見栄えを良くする）
st.markdown("""
    <style>
    .ai-report-card {
        background-color: #f8fafc;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .badge {
        background-color: #3B82F6;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧭 チームナビ Pro")
st.caption("生成AIがメンバーの個性を多角的に分析し、化学反応を予測する次世代ナビゲーション。")

# --- 【超重要】APIキーの設定エリア ---
# ※まずはここにステップ1で取得した鍵を貼り付けてみてください。
# （GitHubに公開する際は、後ほど安全な設定方法に変えます）
# --- 安全なAPIキーの読み込み設定 ---
import os

# Streamlitの金庫（Secrets）から鍵を探す
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = None

# 鍵が見つかればAIを起動する
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("APIキーが設定されていません。Streamlit CloudのSettingsから設定してください

# サイドバー：APIキーの直接入力も可能にしておく（安全対策）
with st.sidebar:
    st.header("⚙️ システム設定")
    user_key = st.text_input("Gemini API Key", type="password", help="Google AI Studioで取得したキーを入力してください")
    if user_key:
        genai.configure(api_key=user_key)
        GOOGLE_API_KEY = user_key

    st.divider()
    st.header("👤 メンバーエントリー")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("名前")
        strength = st.text_input("強み（例：データ分析、チームマネジメント、営業）")
        hobby = st.text_input("趣味（例：サウナ、クラフトビール、ゴルフ）")
        boom = st.text_input("マイブーム（例：生成AI、読書、宅トレ）")
        submitted = st.form_submit_button("ナビに登録")
        if submitted and name:
            if 'member_list' not in st.session_state:
                st.session_state.member_list = []
            st.session_state.member_list.append({
                "名前": name, "強み": strength, "趣味": hobby, "マイブーム": boom
            })

# 2名以上登録されるまで待機
if 'member_list' not in st.session_state or len(st.session_state.member_list) < 2:
    st.info("💡 分析を開始するには、サイドバーから2名以上のメンバーを登録してください。")
    st.stop()

df = pd.DataFrame(st.session_state.member_list)

# --- タブ構成 ---
tab1, tab2 = st.tabs(["🤝 AI深層相性診断", "📊 メンバー一覧"])

with tab1:
    st.subheader("🤖 Geminiが紐解くメンバーシナジー")
    st.write("登録されたデータに基づき、AIが二人の『隠れた共通点』や『ビジネス上の化学反応』を丁寧に分析します。")
    
    # 2人の全組み合わせをループ処理
    for p1, p2 in itertools.combinations(st.session_state.member_list, 2):
        st.markdown(f"### 👥 {p1['名前']} × {p2['名前']}")
        
        # AI分析を実行するボタン（毎回APIを叩くと重いので、ボタン式にするか自動にするか）
        button_key = f"analyze_{p1['名前']}_{p2['名前']}"
        if st.button(f"🔍 {p1['名前']}さんと{p2['名前']}さんの相性をAI分析", key=button_key):
            with st.spinner("AIがプロファイルを熟読中..."):
                try:
                    # AIへの指示（プロンプト）の設計
                    prompt = f"""
                    あなたは組織開発とチームビルディングの専門家（MBAホルダー）です。
                    以下の2人のメンバーのプロフィール（名前、強み、趣味、マイブーム）を読み込み、
                    二人が出会うことで生まれる「化学反応」や「意外な共通点」を、優しく、かつ論理的に丁寧に分析してください。

                    【メンバー1】
                    名前: {p1['名前']} / 強み: {p1['強み']} / 趣味: {p1['趣味']} / マイブーム: {p1['マイブーム']}

                    【メンバー2】
                    名前: {p2['名前']} / 強み: {p2['強み']} / 趣味: {p2['趣味']} / マイブーム: {p2['マイブーム']}

                    【出力形式】
                    以下の3つの項目で、具体的かつユーモアを交えて出力してください。
                    1. 予測される二人のコンビ名・キャッチコピー
                    2. 二人が掛け合わさることで生まれるビジネスシナジー（強みの補完関係など）
                    3. 飲み会で絶対に盛り上がる「二人の共通トークテーマ」の提案
                    """
                    
                    # 最新の軽量・高速モデル「gemini-1.5-flash」を使用
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    
                    # 分析結果をカード形式で表示
                    st.markdown(f"""
                    <div class="ai-report-card">
                        {response.text.replace("\n", "<br>")}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"分析中にエラーが発生しました。APIキーが正しいか確認してください。: {e}")

with tab2:
    st.subheader("📋 登録メンバー一覧")
    st.dataframe(df, use_container_width=True, hide_index=True)
import streamlit as st
import pandas as pd
import collections

# ページ設定
st.set_page_config(page_title="チームナビ", page_icon="🧭", layout="wide")

st.title("🧭 チームナビ：分析ダッシュボード")
st.caption("チームの強みを可視化し、最高のシナジーを生み出すナビゲーション。")

# --- データ管理（セッション状態） ---
if 'member_list' not in st.session_state:
    st.session_state.member_list = []

# サイドバー：データ入力
with st.sidebar:
    st.header("👤 メンバー登録")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("名前")
        strength = st.text_input("強み（例: データ分析, プレゼン）")
        hobby = st.text_input("趣味（例: サウナ, 旅行）")
        boom = st.text_input("マイブーム（例: ChatGPT）")
        submitted = st.form_submit_button("登録")
        if submitted and name:
            st.session_state.member_list.append({
                "名前": name, "強み": strength, "趣味": hobby, "マイブーム": boom
            })

# データが溜まっていない時の表示
if len(st.session_state.member_list) < 2:
    st.info("分析を開始するには、あと " + str(2 - len(st.session_state.member_list)) + " 名の登録が必要です。")
    st.stop()

df = pd.DataFrame(st.session_state.member_list)

# --- 3大分析機能タブ ---
tab1, tab2, tab3 = st.tabs(["🤝 相性分析", "💪 チームの強み", "💬 話題分析"])

# 1. 相性分析機能（シナジー・マッチング）
with tab1:
    st.subheader("相性・シナジー予測")
    st.write("個々の特性を掛け合わせた、おすすめのコンビを提案します。")
    
    # ロジック：共通の趣味、または異なる強みを持つペアを抽出
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            p1, p2 = df.iloc[i], df.iloc[j]
            # 趣味が同じ場合
            if p1['趣味'] == p2['趣味']:
                st.success(f"✨ **趣味共鳴ペア：{p1['名前']} × {p2['名前']}**")
                st.write(f"共通の趣味『{p1['趣味']}』で盛り上がること間違いなし！")
            # 強みが異なる場合（MBA的補完関係）
            else:
                st.info(f"🚀 **ビジネス・シナジーペア：{p1['名前']} × {p2['名前']}**")
                st.write(f"『{p1['強み']}』と『{p2['強み']}』を掛け合わせれば、新しいDXプロジェクトが生まれるかも？")

# 2. チームの強み分析（組織資産の可視化）
with tab2:
    st.subheader("チームのスキルマップ")
    # 単語の出現頻度を簡易分析
    all_strengths = ",".join(df['強み']).replace("、", ",").split(",")
    counts = collections.Counter([s.strip() for s in all_strengths if s.strip()])
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("**主要な強みランキング**")
        for word, count in counts.most_common(5):
            st.write(f"- {word}: {count}名")
    with col2:
        # DX・MBA視点のコメント
        st.metric(label="チームの多様性スコア", value=f"{len(counts)} スキル")
        st.write("💡 **組織分析アドバイス：**")
        if len(counts) > len(df):
            st.write("多才なメンバーが集まっています。個々の専門性を活かしたタスクアサインが効果的です。")
        else:
            st.write("特定の強みに特化したチームです。共通言語があるため、意思決定のスピードが速い傾向にあります。")

# 3. 話題分析（会話のきっかけガチャ）
with tab3:
    st.subheader("今夜のトークテーマ")
    st.write("データから抽出した、飲み会が盛り上がる「お題」です。")
    
    # ランダムにキーワードを拾って話題を作る
    target_member = df.sample(1).iloc[0]
    st.markdown(f"""
    > **【話題のパス】**
    > **「{target_member['名前']}さんのマイブーム『{target_member['マイブーム']}』について、
    > 隣の人は深掘りしてみてください！」**
    """)
    
    if st.button("次のお題を出す"):
        st.rerun()

st.divider()
st.subheader("📋 メンバー一覧")
st.dataframe(df, use_container_width=True, hide_index=True)
# ページ設定（ブラウザのタブに表示される名前とアイコン）
st.set_page_config(page_title="Team Bonding App", page_icon="🥂")

# 背景色やフォントを少しリッチにする（簡易カスタムCSS）
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥂 チームナビ")
st.caption("みんなの『得意』や『好き』を掛け合わせて、新しい話題を見つけよう！")

# 入力フォームをカード風にする
with st.container():
    with st.form("my_form"):
        st.subheader("📝 あなたのことを教えてください")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("名前（ニックネーム）", placeholder="例：モトキ")
            strength = st.text_input("強み・得意", placeholder="例：データ分析、料理")
        with col2:
            hobby = st.text_input("趣味", placeholder="例：サウナ、海外旅行")
            boom = st.text_input("マイブーム", placeholder="例：ChatGPTで画像生成")
            
        submitted = st.form_submit_button("みんなとつながる！")
        if submitted:
            st.balloons() # 登録完了時にお祝いの風船を飛ばす演出
            st.success(f"ありがとう、{name}さん！みんなのリストに追加されました。")

# ネットワーク図や分析結果のプレースホルダー（将来的にAI連携）
st.divider()
st.subheader("🔍 今日の注目つながり")
st.info("💡 **『サウナ』**が趣味の人が3人います！おすすめの施設について話してみては？")

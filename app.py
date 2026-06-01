
import streamlit as st
import pandas as pd
import itertools
import collections
import google.generativeai as genai

# 1. ページ設定
st.set_page_config(page_title="チームナビ Pro", page_icon="🧭", layout="wide")

# 2. デザイン（CSS）
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .ai-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #3B82F6; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 安全なAPIキーの読み込み（エラーが出にくいシンプルな書き方に変更）
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.sidebar.error("API Key not found in Secrets.")

# 4. データ保持
if 'member_list' not in st.session_state:
    st.session_state.member_list = []

st.title("🧭 チームナビ Pro")
st.markdown("### 〜 AIが導く、チームの新しい可能性 〜")

# 5. サイドバー：登録フォーム
with st.sidebar:
    st.header("👤 メンバー登録")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("名前")
        strength = st.text_input("強み")
        hobby = st.text_input("趣味")
        boom = st.text_input("マイブーム")
        submitted = st.form_submit_button("登録")
        if submitted and name:
            st.session_state.member_list.append({
                "名前": name, "強み": strength, "趣味": hobby, "マイブーム": boom
            })

# 6. 分析画面
if len(st.session_state.member_list) < 2:
    st.info("2名以上の登録で分析を開始します。")
    st.stop()

df = pd.DataFrame(st.session_state.member_list)
tab1, tab2, tab3 = st.tabs(["🤝 AI相性診断", "📊 強み分析", "💬 話題ガチャ"])

with tab1:
    st.subheader("🤖 AIによる深層シナジー分析")
    if not GOOGLE_API_KEY:
        st.warning("APIキーが設定されていません。")
    else:
        for p1, p2 in itertools.combinations(st.session_state.member_list, 2):
            st.markdown(f"#### 👥 {p1['名前']} × {p2['名前']}")
            if st.button(f"分析する ({p1['名前']} & {p2['名前']})", key=f"btn_{p1['名前']}_{p2['名前']}"):
                with st.spinner("AIが考案中..."):
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"組織開発のプロとして{p1['名前']}と{p2['名前']}の相性を分析して。趣味:{p1['趣味']}/{p2['趣味']}、強み:{p1['強み']}/{p2['強み']}"
                    response = model.generate_content(prompt)
                    st.markdown(f'<div class="ai-card">{response.text}</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("💪 チームのスキルマップ")
    all_s = [s.strip() for s in ",".join(df['強み']).replace("、", ",").split(",") if s.strip()]
    st.bar_chart(pd.Series(all_s).value_counts())

with tab3:
    st.subheader("🎲 トークテーマ")
    if st.button("話題を振る"):
        pair = df.sample(2)
        st.info(f"{pair.iloc[0]['名前']}さんから{pair.iloc[1]['名前']}さんに『{pair.iloc[1]['マイブーム']}』について聞いてみよう！")

st.divider()
st.dataframe(df, use_container_width=True, hide_index=True)

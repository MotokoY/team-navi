import streamlit as st
import pandas as pd
import itertools
import google.generativeai as genai

# --- 1. ページ設定 ---
st.set_page_config(page_title="チームナビ Pro", layout="wide")

# --- 2. 安全なAPIキーの読み込みと設定 ---
# ここで名前の定義（NameError）が起きないように確実に設定します
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    has_api_key = True
else:
    has_api_key = False

# --- 3. データ管理 ---
if 'member_list' not in st.session_state:
    st.session_state.member_list = []

st.title("🧭 チームナビ Pro")

# --- 4. サイドバー：メンバー登録 ---
with st.sidebar:
    st.header("👤 メンバー登録")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("名前")
        strength = st.text_input("強み")
        hobby = st.text_input("趣味")
        submitted = st.form_submit_button("登録")
        if submitted and name:
            st.session_state.member_list.append({"名前": name, "強み": strength, "趣味": hobby})

# --- 5. メイン画面 ---
if len(st.session_state.member_list) < 2:
    st.info("2名以上のメンバーを登録してください。")
    st.stop()

tab1, tab2 = st.tabs(["🤝 AI相性分析", "📋 メンバー一覧"])

with tab1:
    st.subheader("🤖 Gemini 1.5 相性診断")
    if not has_api_key:
        st.error("APIキーが設定されていません。StreamlitのSecretsを確認してください。")
    else:
        for p1, p2 in itertools.combinations(st.session_state.member_list, 2):
            st.markdown(f"#### 👥 {p1['名前']} × {p2['名前']}")
            if st.button(f"分析する ({p1['名前']} & {p2['名前']})", key=f"btn_{p1['名前']}_{p2['名前']}"):
                try:
                    with st.spinner("AIが考え中..."):
                        # モデル名を最新の安定版に固定
                        model = genai.GenerativeModel('models/gemini-1.5-flash')
                        prompt = f"{p1['名前']}（強み:{p1['強み']}）と{p2['名前']}（強み:{p2['強み']}）のビジネス相性を100文字で分析して。"
                        response = model.generate_content(prompt)
                        st.success(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

with tab2:
    st.dataframe(pd.DataFrame(st.session_state.member_list), use_container_width=True)

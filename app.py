import streamlit as st
import pandas as pd

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
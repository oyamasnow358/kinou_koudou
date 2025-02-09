import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import os
import matplotlib.font_manager as fm  # 日本語フォント設定に必要

# Streamlit Cloud 環境用のフォントパス
font_path = "/app/ipaexg.ttf"

# フォントファイルがあるかチェック
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    matplotlib.rc('font', family=font_prop.get_name())  # フォントを適用
    st.write("✅ 日本語フォントが設定されました！")
else:
    st.error("❌ フォントファイルが見つかりません。サーバーに `ipaexg.ttf` をアップロードしてください。")

# matplotlibのフォント設定
matplotlib.rcParams['font.family'] = font_prop.get_name() if os.path.exists(font_path) else 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け防止

# アプリタイトル
st.title("FBA（機能的行動評価）分析アプリ")

st.markdown("""
このアプリでは、FBA（機能的行動評価）のデータを基にした分析を行います。
**FBA（Functional Behavior Assessment）**とは、行動の目的や理由を特定するための方法です。
""")

# CSVテンプレート
template_csv = """Date（日付）,Behavior（行動）,Antecedent（きっかけ/先行事象）,Consequence（結果/後続事象）,Function（行動の機能）
2025-02-01,Tantrum（かんしゃく）,Requested to stop playing（遊びをやめるように要求された）,Gained attention（注意を向けられた）,Gain Attention（注意を引く）
2025-02-01,Run away（逃げ出す）,Given a task（課題を与えられた）,Ignored（無視された）,Escape（逃避）
"""

st.download_button(
    label="CSVテンプレートをダウンロード",
    data=template_csv.encode('utf-8-sig'),
    file_name="fba_template.csv",
    mime="text/csv"
)

# CSVアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        st.subheader("アップロードされたデータ")
        st.dataframe(df)

        # 行動の頻度
        st.subheader("行動の頻度")
        behavior_counts = df["Behavior（行動）"].value_counts()
        st.bar_chart(behavior_counts)

        # 前駆要因ごとの頻度
        st.subheader("前駆要因ごとの頻度")
        antecedent_counts = df.groupby(["Antecedent（きっかけ/先行事象）", "Behavior（行動）"]).size().unstack(fill_value=0)
        st.dataframe(antecedent_counts)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(antecedent_counts, annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_title("前駆要因ごとの行動頻度", fontproperties=font_prop)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {e}")
else:
    st.info("CSVファイルをアップロードしてください。")

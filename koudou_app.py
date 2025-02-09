import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# 日本語フォントの設定
import matplotlib
matplotlib.rc('font', family='IPAexGothic')  # 日本語フォントを指定

# アプリタイトル
st.title("FBA（機能的行動評価）分析アプリ")

st.markdown("""
このアプリでは、FBA（機能的行動評価）のデータを基にした分析を行います。
まず、CSVテンプレートをダウンロードし、データを入力した後にアップロードしてください。
""")

# CSVテンプレート
template_csv = """日付,行動,きっかけ（先行事象）,結果（後続事象）,行動の機能
2025-02-01,かんしゃく,遊びをやめるように要求された,注意を向けられた,注意を引く
2025-02-01,逃げ出す,課題を与えられた,無視された,逃避
2025-02-02,大声を出す,要求を拒否された,要求が通った,具体的なものを得る
2025-02-03,叩く,宿題をするように求められた,休憩が与えられた,逃避
2025-02-04,物を投げる,アイテムへのアクセスを拒否された,要求が通った,具体的なものを得る
"""

# CSVテンプレートのダウンロード
st.markdown("### CSVテンプレートのダウンロード")
st.download_button(
    label="CSVテンプレートをダウンロード",
    data=template_csv.encode('utf-8-sig'),
    file_name="fba_template.csv",
    mime="text/csv"
)

st.markdown("---")

# CSVアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    try:
        # CSVデータ読み込み
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

        # データ表示
        st.subheader("アップロードされたデータ")
        st.dataframe(df)

        # 列名の確認
        required_columns = ["日付", "行動", "きっかけ（先行事象）", "結果（後続事象）", "行動の機能"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"以下の列が不足しています: {', '.join(missing_columns)}")
        else:
            st.success("データが正常に読み込まれました！")

            # 行動の頻度
            st.subheader("行動の頻度")
            behavior_counts = df["行動"].value_counts()
            st.bar_chart(behavior_counts)

            # 前駆要因ごとの頻度
            st.subheader("前駆要因ごとの頻度")
            antecedent_counts = df.groupby(["きっかけ（先行事象）", "行動"]).size().unstack(fill_value=0)
            st.dataframe(antecedent_counts)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(antecedent_counts, annot=True, fmt="d", cmap="Blues", ax=ax)
            ax.set_title("前駆要因ごとの行動頻度")
            st.pyplot(fig)

            # 結果ごとの頻度
            st.subheader("結果ごとの頻度")
            consequence_counts = df.groupby(["結果（後続事象）", "行動"]).size().unstack(fill_value=0)
            st.dataframe(consequence_counts)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(consequence_counts, annot=True, fmt="d", cmap="Oranges", ax=ax)
            ax.set_title("結果ごとの行動頻度")
            st.pyplot(fig)

            # 行動機能の割合
            st.subheader("行動機能の割合")
            function_counts = df["行動の機能"].value_counts()
            st.dataframe(function_counts)

            fig, ax = plt.subplots()
            function_counts.plot.pie(autopct="%1.1f%%", ax=ax, startangle=90, cmap="viridis")
            ax.set_title("行動の機能の割合")
            ax.set_ylabel("")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"データの読み込みまたは処理中にエラーが発生しました: {e}")
else:
    st.info("CSVファイルをアップロードしてください。")
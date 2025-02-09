import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams  # 修正箇所
import os
import matplotlib.font_manager as fm  # 日本語フォントの設定に必要

# ダウンロードしたフォントのパスを指定
font_path = "C:\Users\taka\OneDrive\デスクトップ\アプリ開発\機能的行動評価\kinou_koudou/ipag.ttf"  # ダウンロードしたフォントファイル名

# フォントファイルが存在するか確認
if os.path.exists(font_path):
    matplotlib.rc('font', family=matplotlib.font_manager.FontProperties(fname=font_path).get_name())
    print("日本語フォントが設定されました！")
else:
    print("フォントファイルが見つかりません。パスを確認してください。")

# アプリタイトル
st.title("FBA（機能的行動評価）分析アプリ")

st.markdown("""
このアプリでは、FBA（機能的行動評価）のデータを基にした分析を行います。
**FBA（Functional Behavior Assessment）**とは、行動の目的や理由を特定するための方法です。  
以下の項目を入力してデータを準備してください：

- **Date（日付）**: 行動が発生した日付
- **Behavior（行動）**: 発生した行動（例: 大声を出す、物を投げる）
- **Antecedent（きっかけ/先行事象）**: 行動が起こる直前の状況や出来事
- **Consequence（結果/後続事象）**: 行動が起きた後に続いた結果
- **Function（行動の機能）**: 行動の目的（例: 注意を引く、逃避）

まず、以下のテンプレートをダウンロードし、データを入力してアップロードしてください。
""")



# CSVテンプレート
template_csv = """Date（日付）,Behavior（行動）,Antecedent（きっかけ/先行事象）,Consequence（結果/後続事象）,Function（行動の機能）
2025-02-01,Tantrum（かんしゃく）,Requested to stop playing（遊びをやめるように要求された）,Gained attention（注意を向けられた）,Gain Attention（注意を引く）
2025-02-01,Run away（逃げ出す）,Given a task（課題を与えられた）,Ignored（無視された）,Escape（逃避）
2025-02-02,Yelling（大声を出す）,Request denied（要求を拒否された）,Request granted（要求が通った）,Obtain Tangible（具体的なものを得る）
2025-02-03,Hitting（叩く）,Asked to do homework（宿題をするように求められた）,Gave a break（休憩が与えられた）,Escape（逃避）
2025-02-04,Throwing objects（物を投げる）,Denied access to item（アイテムへのアクセスを拒否された）,Request granted（要求が通った）,Obtain Tangible（具体的なものを得る）
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
        required_columns = ["Date（日付）", "Behavior（行動）", "Antecedent（きっかけ/先行事象）", "Consequence（結果/後続事象）", "Function（行動の機能）"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"以下の列が不足しています: {', '.join(missing_columns)}")
        else:
            st.success("データが正常に読み込まれました！")

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
            ax.set_title("前駆要因ごとの行動頻度")
            st.pyplot(fig)

            # 結果ごとの頻度
            st.subheader("結果ごとの頻度")
            consequence_counts = df.groupby(["Consequence（結果/後続事象）", "Behavior（行動）"]).size().unstack(fill_value=0)
            st.dataframe(consequence_counts)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(consequence_counts, annot=True, fmt="d", cmap="Oranges", ax=ax)
            ax.set_title("結果ごとの行動頻度")
            st.pyplot(fig)

            # 行動機能の割合
            st.subheader("行動機能の割合")
            function_counts = df["Function（行動の機能）"].value_counts()
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

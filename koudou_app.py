import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# タイトルと概要
st.title("FBA（機能的行動評価）分析アプリ")
st.markdown("""
このアプリでは、FBA（機能的行動評価）のデータをアップロードし、
行動のパターンや前駆要因、結果などを分析して視覚化します。
データを準備してCSV形式でアップロードしてください。
""")

# データアップロード
st.sidebar.header("データアップロード")
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    # データの読み込み
    df = pd.read_csv(uploaded_file)

    st.subheader("アップロードしたデータ")
    st.dataframe(df)

    # 必須列の確認
    required_columns = ["Date", "Behavior", "Antecedent", "Consequence", "Function"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"以下の列が不足しています: {', '.join(missing_columns)}")
    else:
        # 日付ごとの行動頻度
        st.subheader("日付ごとの行動頻度")
        df["Date"] = pd.to_datetime(df["Date"])
        behavior_counts = df.groupby(["Date", "Behavior"]).size().unstack(fill_value=0)

        st.bar_chart(behavior_counts)

        # 前駆要因ごとの行動頻度
        st.subheader("前駆要因ごとの行動頻度")
        antecedent_counts = df.groupby(["Antecedent", "Behavior"]).size().unstack(fill_value=0)
        st.dataframe(antecedent_counts)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(antecedent_counts, annot=True, fmt="d", cmap="Blues", ax=ax)
        st.pyplot(fig)

        # 結果ごとの行動頻度
        st.subheader("結果ごとの行動頻度")
        consequence_counts = df.groupby(["Consequence", "Behavior"]).size().unstack(fill_value=0)
        st.dataframe(consequence_counts)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(consequence_counts, annot=True, fmt="d", cmap="Oranges", ax=ax)
        st.pyplot(fig)

        # 行動の機能ごとの割合
        st.subheader("行動の機能ごとの割合")
        function_counts = df["Function"].value_counts()
        st.dataframe(function_counts)

        fig, ax = plt.subplots()
        function_counts.plot.pie(autopct="%1.1f%%", ax=ax, startangle=90, cmap="viridis")
        ax.set_ylabel("")
        st.pyplot(fig)

        # 詳細な分析
        st.subheader("詳細な分析")
        selected_behavior = st.selectbox("分析したい行動を選択してください", df["Behavior"].unique())
        behavior_data = df[df["Behavior"] == selected_behavior]

        st.markdown(f"### 選択された行動: {selected_behavior}")

        antecedent_behavior_counts = behavior_data["Antecedent"].value_counts()
        st.bar_chart(antecedent_behavior_counts)

        consequence_behavior_counts = behavior_data["Consequence"].value_counts()
        st.bar_chart(consequence_behavior_counts)

else:
    st.info("左側のサイドバーからCSVファイルをアップロードしてください。")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# タイトルと概要
st.title("FBA（機能的行動評価）分析アプリ")
st.markdown("""
このアプリでは、FBA（機能的行動評価）のデータ（CSV）をダウンロードし、それに合わせた形
でアップロードすることで行動のパターンや前駆要因、結果などを分析して視覚化します。
""")

# ------------------------------------------
# CSVテンプレート作成用の文字列（日本語版）
template_csv = """日付,行動,きっかけ（先行事象）,結果（後続事象）,行動の機能
2025-02-01,かんしゃく,遊びをやめるように要求された,注意を向けられた,注意を引く
2025-02-01,逃げ出す,課題を与えられた,無視された,逃避
2025-02-02,大声を出す,要求を拒否された,要求が通った,具体的なものを得る
2025-02-03,叩く,宿題をするように求められた,休憩が与えられた,逃避
2025-02-04,物を投げる,アイテムへのアクセスを拒否された,要求が通った,具体的なものを得る
"""

# ------------------------------------------
# CSVテンプレートダウンロードボタンの設置
st.markdown("### CSVテンプレートのダウンロード")
st.download_button(
    label="CSVテンプレートをダウンロード",
    data=template_csv.encode('utf-8-sig'),
    file_name="fba_template_jp.csv",
    mime="text/csv"
)

st.markdown("---")

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

if uploaded_file is not None:
    try:
        # データ読み込み
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

        # 必須列のチェック
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"次の列が不足しています: {', '.join(missing_columns)}")
        else:
            st.success("データが正常に読み込まれました！")
            st.dataframe(df)

            # 行動別頻度分析
            st.markdown("### 行動ごとの頻度")
            behavior_counts = df["Behavior"].value_counts()
            st.bar_chart(behavior_counts)

            # 強化条件分析
            st.markdown("### 強化される行動の条件")
            condition_analysis = df.groupby(["Antecedent", "Consequence", "Function"])["Behavior"].count().reset_index()
            condition_analysis.rename(columns={"Behavior": "Frequency"}, inplace=True)
            st.write("**条件ごとの行動頻度**")
            st.dataframe(condition_analysis)

            st.write("**解説:** 以下の条件で問題行動が強化される可能性があります。")
            for i, row in condition_analysis.iterrows():
                st.write(
                    f"- **前兆**: {row['Antecedent']} → **結果**: {row['Consequence']} → **機能**: {row['Function']} → **頻度**: {row['Frequency']}"
                )

            # ヒートマップの描画
            st.markdown("### 強化条件のヒートマップ")
            heatmap_data = pd.crosstab(df["Antecedent"], df["Consequence"])
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlOrBr", ax=ax)
            ax.set_title("前兆と結果の関係（ヒートマップ）")
            st.pyplot(fig)

            # 行動の機能分布
            st.markdown("### 行動の機能（Function）の分布")
            function_counts = df["Function"].value_counts()
            st.bar_chart(function_counts)

            # 自動分析レポート生成
            st.markdown("### 自動生成された分析レポート")
            st.write("以下はデータを基に生成された分析結果です。")

            for behavior in df["Behavior"].unique():
                behavior_data = df[df["Behavior"] == behavior]
                common_antecedent = behavior_data["Antecedent"].mode().values[0]
                common_consequence = behavior_data["Consequence"].mode().values[0]
                common_function = behavior_data["Function"].mode().values[0]
                st.write(
                    f"- **行動**: {behavior} は、以下の条件で最も強化される傾向があります。\n"
                    f"  - **前兆**: {common_antecedent}\n"
                    f"  - **結果**: {common_consequence}\n"
                    f"  - **機能**: {common_function}\n"
                )

    except Exception as e:
        st.error(f"ファイルの読み込みに失敗しました: {e}")
else:
    st.info("CSVファイルをアップロードしてください。")


else:
    st.info("左側のサイドバーからCSVファイルをアップロードしてください。")

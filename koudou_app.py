import streamlit as st
import pandas as pd
import plotly.express as px

# --- ページ設定 ---
st.set_page_config(
    page_title="FBA（機能的行動評価）分析アプリ",
    page_icon="🧩",
    layout="wide",
)

# --- アプリタイトルと説明 ---
st.title("🧩 FBA（機能的行動評価）分析アプリ")
st.write("ABC記録法のデータをアップロードし、行動の背景にある機能（理由）を可視化・分析します。")

with st.expander("🤔 FBA（機能的行動評価）とは？ - 初心者向け解説"):
    st.markdown("""
    ### **1. そもそも「機能的アセスメント」って何？**
    簡単にいうと、「**どうしてその行動をするのか？**」という行動の理由や目的（＝機能）を調べることです。
    例えば、授業中に席を立ってしまう子がいるとき、ただ「座りなさい！」と注意するだけでなく、「なぜ席を立ってしまうのか？」の背景を探るのが機能的アセスメントです。

    ### **2. 行動には必ず「目的」がある**
    人の行動は、多くの場合、何か良い結果を得るため（または嫌なことを避けるため）に行われます。
    - **注目を得るため**: 席を立つと先生や友達がかまってくれる。
    - **嫌なことから逃れるため**: 難しい課題から逃れるために席を立つ。
    - **欲しいものを手に入れるため**: おもちゃが欲しくて泣き叫ぶ。
    - **感覚的な刺激を得るため**: 揺れるのが楽しくて体を揺らす。

    このように、一見「問題」に見える行動にも、本人なりの目的や理由が隠されています。

    ### **3. どうやって調べるの？ (ABC記録法)**
    このアプリでは、行動の前後関係を記録する「**ABC記録法**」に基づいたデータを分析します。
    - **A (Antecedent) = 先行事象**: 行動が起こる**直前の状況**（きっかけ）。
      - 例: 「難しい課題が出された」「お母さんが電話を始めた」
    - **B (Behavior) = 行動**: 具体的に**どんな行動**をしたか。
      - 例: 「席を立った」「大声を出した」
    - **C (Consequence) = 後続事象**: 行動の**直後に起きたこと**（結果）。
      - 例: 「先生に注意された」「課題が免除された」

    このA-B-Cの関係を分析することで、行動の「機能」を推測し、より効果的な支援策を考える手助けとなります。
    """)

st.markdown("---")

# --- データ準備セクション ---
st.header("1. データの準備")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📥 CSVテンプレート")
    st.write("以下のテンプレートを参考にデータをご準備ください。")
    template_csv = """日付,行動,きっかけ/先行事象,結果/後続事象,行動の機能
2025-02-01,かんしゃく,遊びをやめるように要求された,注目を得られた,注目要求
2025-02-01,逃げ出す,課題を与えられた,課題から逃れられた,逃避・回避
2025-02-02,大声を出す,要求を拒否された,要求が通った,要求・物品獲得
2025-02-03,叩く,宿題をするように求められた,休憩が与えられた,逃避・回避
2025-02-04,物を投げる,おもちゃを片付けるよう言われた,注目を得られた,注目要求
"""
    st.download_button(
        label="📄 CSVテンプレートをダウンロード",
        data=template_csv.encode('utf-8-sig'),
        file_name="fba_template.csv",
        mime="text/csv"
    )

with col2:
    st.subheader("📤 CSVファイルのアップロード")
    st.write("準備したCSVファイルをここにアップロードしてください。")
    uploaded_file = st.file_uploader("ファイルを選択...", type="csv", label_visibility="collapsed")

# --- ファイルがアップロードされていない場合の表示 ---
if uploaded_file is None:
    st.info("☝️ CSVファイルをアップロードすると、ここに分析結果が表示されます。")
    st.stop()

# --- 分析セクション ---
try:
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

    required_columns = ["行動", "きっかけ/先行事象", "結果/後続事象", "行動の機能"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ ファイルエラー: 必須の列が不足しています。 -> `{', '.join(missing_columns)}`")
        st.stop()
    else:
        st.success("✅ データが正常に読み込まれました！")
        with st.expander("読み込んだデータのプレビュー"):
            st.dataframe(df)

except Exception as e:
    st.error(f"❌ ファイルの読み込み中にエラーが発生しました: {e}")
    st.stop()

st.markdown("---")
st.header("2. 分析結果の可視化")

# --- 頻度と割合の分析 ---
st.subheader("📊 行動の頻度と機能の割合")
col1, col2 = st.columns(2)

with col1:
    # 行動の頻度 (棒グラフ)
    behavior_counts = df["行動"].value_counts().reset_index()
    behavior_counts.columns = ['行動', '回数']
    fig_bar = px.bar(
        behavior_counts,
        x='行動',
        y='回数',
        title='行動の発生頻度',
        text_auto=True,
        color='行動',
        labels={'行動': '行動の種類', '回数': '発生回数'}
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # 行動機能の割合 (円グラフ)
    function_counts = df["行動の機能"].value_counts().reset_index()
    function_counts.columns = ['機能', '回数']
    fig_pie = px.pie(
        function_counts,
        names='機能',
        values='回数',
        title='行動の機能（目的）の割合',
        hole=0.3, # ドーナツグラフにする
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- 関連性の分析 (ヒートマップ) ---
st.subheader("🔍 きっかけ・結果と行動の関連性")
col3, col4 = st.columns(2)

with col3:
    # きっかけごとの頻度 (ヒートマップ)
    antecedent_counts = df.pivot_table(index="きっかけ/先行事象", columns="行動", aggfunc="size", fill_value=0)
    fig_heat_ante = px.imshow(
        antecedent_counts,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='Blues',
        title='【きっかけ → 行動】の関連性ヒートマップ',
        labels=dict(x="行動", y="きっかけ/先行事象", color="回数")
    )
    st.plotly_chart(fig_heat_ante, use_container_width=True)

with col4:
    # 結果ごとの頻度 (ヒートマップ)
    consequence_counts = df.pivot_table(index="結果/後続事象", columns="行動", aggfunc="size", fill_value=0)
    fig_heat_cons = px.imshow(
        consequence_counts,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='Oranges',
        title='【行動 → 結果】の関連性ヒートマップ',
        labels=dict(x="行動", y="結果/後続事象", color="回数")
    )
    st.plotly_chart(fig_heat_cons, use_container_width=True)
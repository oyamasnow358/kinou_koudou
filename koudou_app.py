import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(
    page_title="FBA 行動分析アプリ (Visual Enhanced)",
    page_icon="🎨",
    layout="wide",
)

# --- スタイル定義（見やすさ向上） ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight:bold; }
    .hypothesis-box {
        background-color: #e8f4f8; padding: 20px; border-radius: 10px;
        border-left: 5px solid #007bff; margin-bottom: 20px;
    }
    .strategy-box {
        background-color: #fff3cd; padding: 20px; border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    /* 凡例のようなスタイル */
    .legend-box {
        padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- サンプルデータ ---
template_csv = """日付,行動,きっかけ/先行事象,結果/後続事象,行動の機能
2025-02-01,かんしゃく,ゲームを終わりにするよう言われた,ゲーム時間が延長された,要求・物品獲得
2025-02-01,離席,プリント課題が配られた,廊下に出されて課題を免れた,逃避・回避
2025-02-02,大声を出す,先生が他の子と話していた,先生に「静かに」と注目された,注目要求
2025-02-03,かんしゃく,お菓子を買ってもらえなかった,お菓子を買ってもらえた,要求・物品獲得
2025-02-04,離席,難しい算数の問題が出た,先生が手伝ってくれた（課題が減った）,逃避・回避
2025-02-05,体を揺らす,暇な時間（手持ち無沙汰）,落ち着いている様子,感覚刺激
2025-02-06,かんしゃく,ゲームを終わりにするよう言われた,ゲーム時間が延長された,要求・物品獲得
2025-02-06,離席,プリント課題が配られた,先生が横について教えた,注目要求
"""

# --- メイン画面 ---
st.title("🎨 行動の「理由」が見える FBA分析アプリ")
st.write("行動の前後関係（A-B-C）を色分けして可視化し、直感的にパターンを把握します。")

# --- サイドバー ---
with st.sidebar:
    st.header("📂 データ入力")
    st.download_button(
        label="📄 CSVテンプレートをDL",
        data=template_csv.encode('utf-8-sig'),
        file_name="fba_template_visual.csv",
        mime="text/csv"
    )
    uploaded_file = st.file_uploader("CSVをアップロード", type="csv")

if uploaded_file is None:
    st.info("👈 サイドバーからCSVファイルをアップロードしてください（サンプルで動作確認できます）。")
    st.stop()

# --- データ読み込み ---
try:
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    # 必須列チェック
    req_cols = ["行動", "きっかけ/先行事象", "結果/後続事象", "行動の機能"]
    if not all(col in df.columns for col in req_cols):
        st.error(f"必須列が不足しています: {req_cols}")
        st.stop()
except Exception as e:
    st.error(f"エラー: {e}")
    st.stop()

# --- 分析対象の選択 ---
st.markdown("---")
col_sel1, col_sel2 = st.columns([1, 3])
with col_sel1:
    st.subheader("🔍 分析対象")
    target_behavior = st.selectbox("詳しく見る行動を選択", df['行動'].unique())

df_target = df[df['行動'] == target_behavior].copy()

if df_target.empty:
    st.stop()

# --- 自動分析レポート（ロジックは前回同様、表示を微調整） ---
with col_sel2:
    st.subheader("📝 分析サマリー")
    top_func = df_target['行動の機能'].mode()[0] if not df_target.empty else "不明"
    top_ante = df_target['きっかけ/先行事象'].mode()[0] if not df_target.empty else "不明"
    
    st.markdown(f"""
    <div class="hypothesis-box">
        <b>💡 AI仮説:</b> <br>
        この行動は、<span style="color:#007bff; font-weight:bold;">「{top_ante}」</span> という状況下で、
        <span style="color:#28a745; font-weight:bold;">「{top_func}」</span> を達成するために行われている傾向があります。
    </div>
    """, unsafe_allow_html=True)

# --- 3. ビジュアルサンキー図（ここがメインの改良） ---
st.markdown("---")
st.header("🌊 行動連鎖のフロー図 (A ➡ B ➡ C)")

st.markdown("""
<div style="display:flex; gap:10px; margin-bottom:10px;">
    <div class="legend-box" style="background-color:#1f77b4; width:30%;">A: きっかけ (Blue)</div>
    <div class="legend-box" style="background-color:#ff7f0e; width:30%;">B: 行動 (Orange)</div>
    <div class="legend-box" style="background-color:#2ca02c; width:30%;">C: 結果 (Green)</div>
</div>
""", unsafe_allow_html=True)

# サンキー図用データ処理
# 1. ノード（登場する単語）をリスト化する際、カテゴリ（A, B, C）を区別して管理する
# これにより、同じ単語がAとCにあっても別のノードとして扱える（色が混ざらない）

# データ集計
sankey_counts = df_target.groupby(['きっかけ/先行事象', '行動', '結果/後続事象']).size().reset_index(name='value')

# ノードリストの作成
# ラベルにスペースなどを追加して、Plotly上で別のノードとして認識させるハック技を使わず、
# 順番にインデックスを管理します。

nodes = []
node_colors = []
labels = []

# Aのノード登録
ante_list = sankey_counts['きっかけ/先行事象'].unique().tolist()
ante_map = {}
for item in ante_list:
    ante_map[item] = len(nodes)
    nodes.append(item)
    labels.append(item)
    node_colors.append("#1f77b4") # Blue

# Bのノード登録
beh_list = sankey_counts['行動'].unique().tolist()
beh_map = {}
for item in beh_list:
    beh_map[item] = len(nodes)
    nodes.append(item)
    labels.append(item)
    node_colors.append("#ff7f0e") # Orange/Red

# Cのノード登録
cons_list = sankey_counts['結果/後続事象'].unique().tolist()
cons_map = {}
for item in cons_list:
    cons_map[item] = len(nodes)
    nodes.append(item)
    labels.append(item)
    node_colors.append("#2ca02c") # Green

# リンク（線）の作成
source = []
target = []
values = []
link_colors = []

# A -> B のリンク
# Aごとのグループを作成してリンクをつなぐ
df_ab = sankey_counts.groupby(['きっかけ/先行事象', '行動'])['value'].sum().reset_index()
for _, row in df_ab.iterrows():
    source.append(ante_map[row['きっかけ/先行事象']])
    target.append(beh_map[row['行動']])
    values.append(row['value'])
    link_colors.append("rgba(31, 119, 180, 0.3)") # Blueの半透明

# B -> C のリンク
df_bc = sankey_counts.groupby(['行動', '結果/後続事象'])['value'].sum().reset_index()
for _, row in df_bc.iterrows():
    source.append(beh_map[row['行動']])
    target.append(cons_map[row['結果/後続事象']])
    values.append(row['value'])
    link_colors.append("rgba(255, 127, 14, 0.3)") # Orangeの半透明

# サンキー図描画
fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color=node_colors, # 指定した色を適用
    ),
    link=dict(
        source=source,
        target=target,
        value=values,
        color=link_colors # 指定した色を適用
    )
)])

fig_sankey.update_layout(
    height=500,
    font_size=14,
    margin=dict(l=10, r=10, t=30, b=30)
)
st.plotly_chart(fig_sankey, use_container_width=True)

# --- その他の詳細グラフ ---
st.markdown("---")
st.subheader("📊 詳細データ分析")

col1, col2 = st.columns(2)

with col1:
    # 機能の円グラフ（パステルカラーで見やすく）
    func_counts = df_target['行動の機能'].value_counts().reset_index()
    func_counts.columns = ['機能', '回数']
    fig_pie = px.pie(
        func_counts, names='機能', values='回数',
        title=f'「{target_behavior}」の目的割合',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel # パステルカラー
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # きっかけの棒グラフ（単色で見やすく）
    ante_counts = df_target['きっかけ/先行事象'].value_counts().reset_index().head(5)
    ante_counts.columns = ['きっかけ', '回数']
    fig_bar = px.bar(
        ante_counts, y='きっかけ', x='回数', orientation='h',
        title='発生しやすい状況 TOP5',
        text_auto=True,
        color_discrete_sequence=['#1f77b4'] # 青系で統一
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 支援アドバイス表示（前回好評だった機能を維持） ---
st.markdown("---")
st.subheader("💡 機能に基づいた対応ヒント")

# 機能特定
main_function = df_target['行動の機能'].mode()[0] if not df_target.empty else ""

# アドバイス辞書
tips = {
    "要求・物品獲得": ("🎁 「ちょうだい」を教えるチャンスです", "行動がおさまってから渡すのではなく、「ちょうだい」とジェスチャーや言葉で伝えた瞬間に渡す練習をしましょう。"),
    "注目要求": ("👀 適切な行動に注目しましょう", "問題行動中は安全を確保しつつ反応を控え、静かにしている時や適切な行動をしている時にたくさん褒めましょう。"),
    "逃避・回避": ("🏃 課題の難易度を見直しましょう", "「手伝って」や「休憩」を言えるように教えるか、課題の量を減らして『できた！』という経験を増やしましょう。"),
    "感覚刺激": ("🌀 代わりの遊びを提供しましょう", "その行動と同じような感覚が得られる、より適切な遊び（スクイーズを握る、トランポリンなど）を用意しましょう。")
}

tip_title, tip_content = tips.get(main_function, ("🤔 専門家にご相談ください", "複数の機能が混ざっている可能性があります。"))

st.info(f"**【{main_function}】へのアプローチ:**\n\n**{tip_title}**\n\n{tip_content}")

with st.expander("全データリストを表示"):
    st.dataframe(df)
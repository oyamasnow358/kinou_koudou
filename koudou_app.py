import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(
    page_title="FBA 行動分析アプリ (修正版)",
    page_icon="🧩",
    layout="wide",
)

# --- CSSスタイル ---
st.markdown("""
<style>
    .big-font { font-size:22px !important; font-weight:bold; }
    .get-box {
        background-color: #e6f9ff; border: 2px solid #00aaff;
        border-radius: 15px; padding: 20px; color: #004d73;
    }
    .escape-box {
        background-color: #fff5e6; border: 2px solid #ff9900;
        border-radius: 15px; padding: 20px; color: #804d00;
    }
    .legend-box {
        padding: 8px; border-radius: 5px; text-align: center; 
        color: white; font-weight: bold; font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- テンプレートデータ（30件） ---
template_csv = """日付,行動,きっかけ/先行事象,結果/後続事象,行動の機能
2025-02-01,かんしゃく,ゲームを終わりにするよう言われた,ゲーム時間が延長された,要求・物品獲得
2025-02-01,離席,算数プリントが配られた,廊下に出されて課題を免れた,逃避・回避
2025-02-02,大声を出す,先生が他の子と話していた,先生に「静かに」と注目された,注目要求
2025-02-02,かんしゃく,お菓子を買ってもらえなかった,お菓子を買ってもらえた,要求・物品獲得
2025-02-03,離席,漢字の書き取り課題が出た,先生が手伝ってくれた（負担減）,逃避・回避
2025-02-03,かんしゃく,YouTubeを消された,YouTubeを見せてくれた,要求・物品獲得
2025-02-04,体を揺らす,暇な時間（手持ち無沙汰）,落ち着いている様子,感覚刺激
2025-02-04,離席,算数プリントが配られた,保健室に行って課題をしなかった,逃避・回避
2025-02-05,大声を出す,自由時間に一人だった,先生が話しかけに来た,注目要求
2025-02-05,かんしゃく,おもちゃを片付けるよう言われた,片付けずに遊べた,逃避・回避
2025-02-06,かんしゃく,ゲームを終わりにするよう言われた,根負けして延長された,要求・物品獲得
2025-02-06,離席,難しい問題に直面した,休憩を挟むことになった,逃避・回避
2025-02-07,大声を出す,先生がパソコン作業をしていた,先生が作業を止めて見た,注目要求
2025-02-07,離席,集団活動（苦手）が始まった,クールダウンスペースへ移動した,逃避・回避
2025-02-08,かんしゃく,スーパーでお菓子を拒否された,お菓子を買ってもらえた,要求・物品獲得
2025-02-08,体を揺らす,待ち時間（退屈）,落ち着いている様子,感覚刺激
2025-02-09,かんしゃく,テレビを消された,テレビをつけてもらえた,要求・物品獲得
2025-02-09,離席,算数プリントが配られた,先生が横について教えた,注目要求
2025-02-10,離席,漢字の書き取り課題が出た,課題をやらなくて済んだ,逃避・回避
2025-02-10,かんしゃく,ゲームを終わりにするよう言われた,あと5分延長された,要求・物品獲得
2025-02-11,大声を出す,先生同士が話していた,「どうしたの？」と聞かれた,注目要求
2025-02-11,離席,嫌いな野菜が出た（給食）,野菜を減らしてもらえた,逃避・回避
2025-02-12,かんしゃく,ガチャガチャを断られた,ガチャガチャをやらせてくれた,要求・物品獲得
2025-02-12,離席,算数プリントが配られた,トイレに逃げ込んだ,逃避・回避
2025-02-13,かんしゃく,タブレットを取り上げられた,タブレットを返してもらえた,要求・物品獲得
2025-02-13,大声を出す,お母さんが電話していた,電話を切って話を聞いてくれた,注目要求
2025-02-14,離席,作文の課題が出た,別室で休むことになった,逃避・回避
2025-02-14,体を揺らす,何もすることがない時,落ち着いている様子,感覚刺激
2025-02-15,かんしゃく,ゲームを終わりにするよう言われた,ゲーム時間が延長された,要求・物品獲得
"""

# --- メインタイトル ---
st.title("🧩 行動の「理由」が見える FBA分析アプリ")
st.write("文字をくっきり表示し、見やすさを向上させたバージョンです。")

# --- サイドバー ---
with st.sidebar:
    st.header("📂 データ入力")
    st.download_button(
        label="📄 サンプルデータをDL",
        data=template_csv.encode('utf-8-sig'),
        file_name="fba_sample_large.csv",
        mime="text/csv"
    )
    uploaded_file = st.file_uploader("CSVをアップロード", type="csv")

if uploaded_file is None:
    st.info("👈 左側のメニューからCSVファイルをアップロードしてください。")
    st.stop()

# --- データ読み込み ---
try:
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    req_cols = ["行動", "きっかけ/先行事象", "結果/後続事象", "行動の機能"]
    if not all(col in df.columns for col in req_cols):
        st.error(f"必須列が不足しています: {req_cols}")
        st.stop()
except Exception as e:
    st.error(f"エラー: {e}")
    st.stop()

# --- 分析対象選択 ---
st.markdown("---")
col_sel, col_empty = st.columns([1, 2])
with col_sel:
    behavior_counts = df['行動'].value_counts()
    target_behavior = st.selectbox("🔍 分析する行動を選択", behavior_counts.index)

df_target = df[df['行動'] == target_behavior].copy()
if df_target.empty: st.stop()

# --- 自動判定ロジック ---
top_func = df_target['行動の機能'].mode()[0]
top_ante = df_target['きっかけ/先行事象'].mode()[0]
reinforcement_type = "unknown"
if top_func in ["要求・物品獲得", "注目要求", "感覚刺激"]:
    reinforcement_type = "positive"
elif top_func in ["逃避・回避"]:
    reinforcement_type = "negative"

# --- 1. 結果表示（カード形式） ---
st.subheader("💡 分析結果：行動のエンジンは何？")

if reinforcement_type == "positive":
    st.markdown(f"""
    <div class="get-box">
        <div class="big-font">➕ 「獲得（ゲット）」タイプ（正の強化）</div>
        <p>行動することで<b>「良いこと」がプラス</b>されています。</p>
        <hr style="border-top: 1px dashed #00aaff;">
        <ul style="font-size:18px;">
            <li><b>きっかけ:</b> {top_ante}</li>
            <li><b>目的:</b> {top_func}</li>
        </ul>
        <div style="font-size:40px; text-align:center;">🎁 🙌 👀</div>
    </div>
    """, unsafe_allow_html=True)

elif reinforcement_type == "negative":
    st.markdown(f"""
    <div class="escape-box">
        <div class="big-font">➖ 「回避（逃げ）」タイプ（負の強化）</div>
        <p>行動することで<b>「嫌なこと」がマイナス</b>されています。</p>
        <hr style="border-top: 1px dashed #ff9900;">
        <ul style="font-size:18px;">
            <li><b>きっかけ:</b> {top_ante}</li>
            <li><b>目的:</b> {top_func}</li>
        </ul>
        <div style="font-size:40px; text-align:center;">🏃💨 🚫 🔚</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 視覚的フロー（サンキー図）くっきり版 ---
st.markdown("---")
st.subheader("🌊 行動の流れ（A ➡ B ➡ C）")

st.markdown("""
<div style="display:flex; gap:10px; margin-bottom:10px;">
    <div class="legend-box" style="background-color:#1f77b4; width:30%;">A: きっかけ (青)</div>
    <div class="legend-box" style="background-color:#ff7f0e; width:30%;">B: 行動 (オレンジ)</div>
    <div class="legend-box" style="background-color:#2ca02c; width:30%;">C: 結果 (緑)</div>
</div>
""", unsafe_allow_html=True)

# サンキー図ロジック
sankey_counts = df_target.groupby(['きっかけ/先行事象', '行動', '結果/後続事象']).size().reset_index(name='value')
nodes = []
node_colors = []
labels = []

def add_nodes(items, color):
    mapping = {}
    for item in items:
        if item not in mapping:
            mapping[item] = len(nodes)
            nodes.append(item)
            labels.append(item)
            node_colors.append(color)
    return mapping

ante_map = add_nodes(sankey_counts['きっかけ/先行事象'].unique(), "#1f77b4")
beh_map = add_nodes(sankey_counts['行動'].unique(), "#ff7f0e")
cons_map = add_nodes(sankey_counts['結果/後続事象'].unique(), "#2ca02c")

source, target, values, link_colors = [], [], [], []

# A->B
df_ab = sankey_counts.groupby(['きっかけ/先行事象', '行動'])['value'].sum().reset_index()
for _, row in df_ab.iterrows():
    source.append(ante_map[row['きっかけ/先行事象']])
    target.append(beh_map[row['行動']])
    values.append(row['value'])
    link_colors.append("rgba(31, 119, 180, 0.4)")

# B->C
df_bc = sankey_counts.groupby(['行動', '結果/後続事象'])['value'].sum().reset_index()
for _, row in df_bc.iterrows():
    source.append(beh_map[row['行動']])
    target.append(cons_map[row['結果/後続事象']])
    values.append(row['value'])
    link_colors.append("rgba(255, 127, 14, 0.4)")

# ★ 修正箇所: nodeの中にtextfontを入れず、update_layoutで全体を設定する ★
fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=25,
        line=dict(color="black", width=0.5),
        label=labels,
        color=node_colors,
        # ここにあった textfont=dict(...) は削除しました（これがエラーの原因）
    ),
    link=dict(source=source, target=target, value=values, color=link_colors)
)])

# ★ ここでフォント設定を一括適用してくっきりさせる ★
fig_sankey.update_layout(
    height=600,
    font=dict(size=16, color="black", family="Arial Black"), # ここでフォントを指定
    margin=dict(l=20, r=20, t=40, b=40)
)
st.plotly_chart(fig_sankey, use_container_width=True)

# --- 3. 対応策 ---
st.markdown("---")
st.subheader("💡 対応アプローチ")

if reinforcement_type == "positive":
    st.info(f"""
    ##### 【➕ 獲得タイプ（正の強化）】
    **「{target_behavior}」以外の方法で「欲しいもの（{top_func}）」を手に入れる練習をしましょう。**
    
    1.  **要求スキル:** 「ちょうだい」「見て」と言葉やカードで伝える練習をする。
    2.  **先回り:** かんしゃくが起きる前に、適切なタイミングで注目したり物を渡したりする。
    """)
elif reinforcement_type == "negative":
    st.warning(f"""
    ##### 【➖ 回避タイプ（負の強化）】
    **「{target_behavior}」以外の方法で「嫌な状況」を変える練習をしましょう。**
    
    1.  **SOSスキル:** 「手伝って」「休憩」と伝える練習をする。
    2.  **環境調整:** 「{top_ante}」の難易度を下げたり、量を減らしたりして成功体験を作る。
    """)

# --- 詳細データ ---
with st.expander("📊 詳細データ（円グラフ・表）"):
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(
            df_target, names='行動の機能', title='機能の割合', hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # 円グラフの文字も大きく・黒く設定
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', 
                              textfont_size=16, textfont_color="black")
        fig_pie.update_layout(font=dict(size=14, family="Arial"))
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.dataframe(df_target, height=350)
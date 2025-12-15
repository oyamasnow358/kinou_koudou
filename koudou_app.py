import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(
    page_title="FBA 行動分析アプリ (データ増量版)",
    page_icon="🧩",
    layout="wide",
)

# --- CSSスタイル（カードデザインの強化） ---
st.markdown("""
<style>
    .big-font { font-size:22px !important; font-weight:bold; }
    /* 獲得（正の強化）用のスタイル */
    .get-box {
        background-color: #e6f9ff; /* 薄い青 */
        border: 2px solid #00aaff;
        border-radius: 15px;
        padding: 20px;
        color: #004d73;
    }
    /* 回避（負の強化）用のスタイル */
    .escape-box {
        background-color: #fff5e6; /* 薄いオレンジ */
        border: 2px solid #ff9900;
        border-radius: 15px;
        padding: 20px;
        color: #804d00;
    }
    .legend-box {
        padding: 8px; border-radius: 5px; text-align: center; color: white; font-weight: bold; font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- テンプレートデータ（30件以上に増量し、傾向を明確化） ---
# パターンA: かんしゃく → ゲーム延長・お菓子GET（獲得＋）
# パターンB: 離席 → 課題からの逃避（回避－）
# パターンC: 大声 → 先生の注目（獲得＋）
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
st.write("「なぜその行動をするのか？」を、**何かを得たい（＋）**のか、**何かから逃れたい（－）**のかに分けて分析します。")

# --- サイドバー ---
with st.sidebar:
    st.header("📂 データ入力")
    st.download_button(
        label="📄 豊富なサンプルデータをDL",
        data=template_csv.encode('utf-8-sig'),
        file_name="fba_sample_large.csv",
        mime="text/csv",
        help="約30件のデータが入っており、分析結果が綺麗に表示されます。"
    )
    uploaded_file = st.file_uploader("CSVをアップロード", type="csv")

if uploaded_file is None:
    st.info("👈 左側のメニューからCSVファイルをアップロードしてください（サンプルDL推奨）。")
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
    # データが多い順に行動をソートして表示
    behavior_counts = df['行動'].value_counts()
    target_behavior = st.selectbox("🔍 分析する行動を選択", behavior_counts.index)

df_target = df[df['行動'] == target_behavior].copy()
if df_target.empty: st.stop()

# --- 自動判定ロジック（ここが核） ---
top_func = df_target['行動の機能'].mode()[0]
top_ante = df_target['きっかけ/先行事象'].mode()[0]

# 機能の分類ロジック
reinforcement_type = "unknown"
if top_func in ["要求・物品獲得", "注目要求", "感覚刺激"]:
    reinforcement_type = "positive"
elif top_func in ["逃避・回避"]:
    reinforcement_type = "negative"

# --- 1. 結果の分かりやすい表示（カード形式） ---
st.subheader("💡 分析結果：行動のエンジンは何？")

if reinforcement_type == "positive":
    st.markdown(f"""
    <div class="get-box">
        <div class="big-font">➕ 「獲得（ゲット）」タイプ（正の強化）</div>
        <p>この行動は、<b>「何か良いこと（メリット）」がプラスされる</b>から繰り返されています。</p>
        <hr style="border-top: 1px dashed #00aaff;">
        <ul>
            <li><b>よくあるきっかけ:</b> {top_ante}</li>
            <li><b>一番の目的:</b> {top_func}</li>
            <li><b>解説:</b> 本人にとって「欲しいものが手に入る」「かまってもらえる」という結果がご褒美になっています。</li>
        </ul>
        <div style="font-size:40px; text-align:center;">🎁 🙌 👀</div>
    </div>
    """, unsafe_allow_html=True)

elif reinforcement_type == "negative":
    st.markdown(f"""
    <div class="escape-box">
        <div class="big-font">➖ 「回避（逃げ）」タイプ（負の強化）</div>
        <p>この行動は、<b>「嫌なこと（デメリット）」がマイナスされる</b>から繰り返されています。</p>
        <hr style="border-top: 1px dashed #ff9900;">
        <ul>
            <li><b>よくあるきっかけ:</b> {top_ante}</li>
            <li><b>一番の目的:</b> {top_func}</li>
            <li><b>解説:</b> 本人にとって「嫌なことが終わる」「やらなくて済む」という結果がご褒美になっています。</li>
        </ul>
        <div style="font-size:40px; text-align:center;">🏃💨 🚫 🔚</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("機能が特定できませんでした。データを確認してください。")

# --- 2. 視覚的フロー（サンキー図） ---
st.markdown("---")
st.subheader("🌊 行動の流れ（A ➡ B ➡ C）")
st.caption("左から右へ、どのような流れで行動が起き、どう終わったかを表示します。太い線ほど多いパターンです。")

# 凡例
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
    link_colors.append("rgba(31, 119, 180, 0.4)") # 少し濃くしました

# B->C
df_bc = sankey_counts.groupby(['行動', '結果/後続事象'])['value'].sum().reset_index()
for _, row in df_bc.iterrows():
    source.append(beh_map[row['行動']])
    target.append(cons_map[row['結果/後続事象']])
    values.append(row['value'])
    link_colors.append("rgba(255, 127, 14, 0.4)") # 少し濃くしました

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels, color=node_colors),
    link=dict(source=source, target=target, value=values, color=link_colors)
)])
fig_sankey.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_sankey, use_container_width=True)

# --- 3. 対応策の提案（タイプ別） ---
st.markdown("---")
st.subheader("💡 どう対応すればいい？")

if reinforcement_type == "positive":
    st.info(f"""
    **【➕ 獲得タイプ（正の強化）へのアプローチ】**
    
    「{target_behavior}」をしなくても、**もっと適切な方法で「欲しいもの（{top_func}）」が手に入る**ことを教えましょう。
    
    1.  **「ちょうだい」「見て」を教える:** 言葉やカードで要求できたら、すぐに叶えてあげます。
    2.  **先回りして与える:** 問題行動が起きる前に、十分に注目したり、好きなものを渡したりしておきます。
    3.  **問題行動には反応しない:** 安全な範囲で、泣いたり暴れたりしても「要求は通らない」ことを一貫して示します。
    """)
elif reinforcement_type == "negative":
    st.warning(f"""
    **【➖ 回避タイプ（負の強化）へのアプローチ】**
    
    「{target_behavior}」をしなくても、**もっと適切な方法で「嫌な状況」を変えられる**ことを教えましょう。
    
    1.  **「手伝って」「休憩」を教える:** 適切なSOSが出せたら、すぐに課題を中断したり手伝ったりします。
    2.  **課題の調整:** 「{top_ante}」が難しすぎたり、長すぎたりしませんか？ 本人が「これならできる」と思えるレベルに調整します。
    3.  **終わりを明確にする:** 「あと3問で終わり」「時計の針がここに来たら終わり」と見通しを持たせます。
    """)
else:
    st.write("データから傾向が読み取れませんでした。")

# --- 詳細データ ---
with st.expander("📊 詳細データを見る（円グラフ・生データ）"):
    col1, col2 = st.columns(2)
    with col1:
        # パステルカラーで見やすい円グラフ
        fig_pie = px.pie(
            df_target, names='行動の機能', title='機能の割合', hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.dataframe(df_target, height=300)
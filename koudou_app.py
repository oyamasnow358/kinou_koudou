import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(
    page_title="FBA 行動の理由分析アプリ",
    page_icon="🧩",
    layout="wide",
)

# --- スタイル定義（見やすさ向上） ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight:bold; }
    .hypothesis-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
    }
    .strategy-box {
        background-color: #fff3cd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# --- テンプレートデータ（より具体的で分かりやすい例） ---
template_csv = """日付,行動,きっかけ/先行事象,結果/後続事象,行動の機能
2025-02-01,かんしゃく,ゲームを終わりにするよう言われた,ゲーム時間が延長された,要求・物品獲得
2025-02-01,離席,プリント課題が配られた,廊下に出されて課題を免れた,逃避・回避
2025-02-02,大声を出す,先生が他の子と話していた,先生に「静かに」と注目された,注目要求
2025-02-03,かんしゃく,お菓子を買ってもらえなかった,お菓子を買ってもらえた,要求・物品獲得
2025-02-04,離席,難しい算数の問題が出た,先生が手伝ってくれた（課題が減った）,逃避・回避
2025-02-05,体を揺らす,暇な時間（手持ち無沙汰）,落ち着いている様子,感覚刺激
"""

# --- アプリタイトルと説明 ---
st.title("🧩 行動の「理由」が見える FBA分析アプリ")
st.markdown("""
お子さんや対象者の行動データを分析し、**「なぜその行動をするのか？（機能）」** を可視化します。
データに基づいた**仮説**と、機能別の**支援のヒント**を提案します。
""")

with st.expander("📚 初めての方へ：ABC記録と機能について"):
    st.markdown("""
    行動を理解するには、前後の状況をセットで見る**ABC分析**が有効です。
    - **A (Antecedent/きっかけ)**: 直前に何があったか？（例: 「勉強しなさい」と言われた）
    - **B (Behavior/行動)**: 何をしたか？（例: ゲームを投げた）
    - **C (Consequence/結果)**: 直後にどうなったか？（例: 叱られた、勉強しなくて済んだ）
    
    これらを分析すると、行動の**機能（目的）**が見えてきます。
    - 🔍 **注目要求**: 見てほしい、かまってほしい
    - 🏃 **逃避・回避**: 嫌なことから逃げたい、やりたくない
    - 🎁 **要求・物品獲得**: 欲しいものが手に入れたい
    - 🌀 **感覚刺激**: その行動自体が心地よい、手持ち無沙汰
    """)

# --- データ準備 ---
st.header("1. データの準備")
with st.sidebar:
    st.header("メニュー")
    st.download_button(
        label="📄 サンプルCSVをダウンロード",
        data=template_csv.encode('utf-8-sig'),
        file_name="fba_template_v2.csv",
        mime="text/csv",
        help="これを編集してアップロードしてください"
    )

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is None:
    st.info("👈 サイドバーからサンプルをDLするか、CSVファイルをアップロードしてください。")
    st.stop()

# --- データ読み込み ---
try:
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    # 空白除去
    df.columns = df.columns.str.strip()
    
    required_columns = ["行動", "きっかけ/先行事象", "結果/後続事象", "行動の機能"]
    missing = [c for c in required_columns if c not in df.columns]
    
    if missing:
        st.error(f"❌ 必要な列が見つかりません: {', '.join(missing)}")
        st.stop()
    else:
        st.success(f"✅ {len(df)}件のデータを読み込みました")

except Exception as e:
    st.error(f"エラー: {e}")
    st.stop()

# --- 分析モード選択 ---
st.markdown("---")
st.header("2. 詳細分析")

# 全体の行動リスト
unique_behaviors = df['行動'].unique()
target_behavior = st.selectbox("分析したい「行動」を選んでください", unique_behaviors)

# 選択された行動のみフィルタリング
df_target = df[df['行動'] == target_behavior]

if not df_target.empty:
    st.markdown(f"### 🎯 「{target_behavior}」の分析結果")
    
    # --- 自動仮説生成ロジック ---
    # 最も多い「機能」と「きっかけ」を抽出
    top_function = df_target['行動の機能'].mode()[0]
    top_antecedent = df_target['きっかけ/先行事象'].mode()[0]
    
    function_count = df_target['行動の機能'].value_counts().max()
    total_count = len(df_target)
    confidence = (function_count / total_count) * 100

    # 仮説文の作成
    st.markdown(f"""
    <div class="hypothesis-box">
        <div class="big-font">🤖 AIによる仮説ステートメント</div>
        <p>データによると、この行動は<b>「{top_antecedent}」</b>という状況で発生しやすく、
        その主な目的（機能）は<b>「{top_function}」</b>である可能性が高いです。
        <br><small>（データの {confidence:.0f}% がこの機能を示しています）</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 支援のヒント（機能に基づくアドバイス） ---
    advice_dict = {
        "注目要求": "**【適切な行動で注目を引けるようにする】**<br>・問題行動は（安全な範囲で）無視し、適切な行動をした瞬間に褒める。<br>・「見て」と口で言えたらすぐに対応する練習をする。",
        "逃避・回避": "**【課題の調整や休憩の導入】**<br>・「手伝って」や「休憩」を適切に言えるように教える。<br>・課題を簡単にする、または短く区切ってスモールステップにする。",
        "要求・物品獲得": "**【適切な要求方法を教える】**<br>・泣いても要求は通らないことを一貫して示す。<br>・「貸して」「ちょうだい」と言葉やカードで伝えたらすぐに渡す。",
        "感覚刺激": "**【代替行動の提案】**<br>・同じような感覚が得られる適切な遊び（トランポリン、スクイーズなど）を提供する。<br>・手持ち無沙汰な時間を減らす。"
    }
    
    # 部分一致でアドバイスを探す
    advice_text = "機能に応じた専門家のアドバイスを求めてください。"
    for key, text in advice_dict.items():
        if key in top_function:
            advice_text = text
            break
            
    st.markdown(f"""
    <div class="strategy-box">
        <div class="big-font">💡 支援のヒント</div>
        <p>{advice_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- グラフ表示 ---
    col1, col2 = st.columns(2)
    
    with col1:
        # きっかけのパレート図
        antecedent_counts = df_target['きっかけ/先行事象'].value_counts().reset_index()
        antecedent_counts.columns = ['きっかけ', '回数']
        fig_ant = px.bar(antecedent_counts, x='回数', y='きっかけ', orientation='h', 
                         title=f'「{target_behavior}」が起きやすい状況', text_auto=True)
        fig_ant.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_ant, use_container_width=True)
        
    with col2:
        # 機能の円グラフ
        function_counts = df_target['行動の機能'].value_counts().reset_index()
        function_counts.columns = ['機能', '回数']
        fig_pie = px.pie(function_counts, names='機能', values='回数', 
                         title=f'「{target_behavior}」の機能（目的）', hole=0.4)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- 全体俯瞰（サンキー図） ---
st.markdown("---")
st.header("3. 全データの流れを見る（サンキー図）")
st.write("「きっかけ ➡ 行動 ➡ 結果」の流れを可視化します。太い線ほど頻度が高いパターンです。")

# サンキー図のデータ作成ロジック
# データフレームを集計
sankey_df = df.groupby(['きっかけ/先行事象', '行動', '結果/後続事象']).size().reset_index(name='value')

# ノード（要素）のリスト作成
all_nodes = list(pd.concat([
    sankey_df['きっかけ/先行事象'], 
    sankey_df['行動'], 
    sankey_df['結果/後続事象']
]).unique())

# ノードをインデックスに変換するマップ
node_map = {node: i for i, node in enumerate(all_nodes)}

# リンク（線）の作成
source = []
target = []
value = []

# A -> B のリンク
for _, row in sankey_df.iterrows():
    source.append(node_map[row['きっかけ/先行事象']])
    target.append(node_map[row['行動']])
    value.append(row['value'])

# B -> C のリンク
for _, row in sankey_df.iterrows():
    source.append(node_map[row['行動']])
    target.append(node_map[row['結果/後続事象']])
    value.append(row['value'])

# サンキー図の描画
fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=all_nodes,
        color="blue"
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color='rgba(0, 0, 255, 0.2)' # 薄い青
    )
)])

fig_sankey.update_layout(title_text="行動の連鎖フロー (A ➡ B ➡ C)", font_size=12, height=500)
st.plotly_chart(fig_sankey, use_container_width=True)

# --- データテーブル ---
with st.expander("📋 生データを確認する"):
    st.dataframe(df)
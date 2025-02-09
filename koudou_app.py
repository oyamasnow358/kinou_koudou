import matplotlib
import matplotlib.font_manager as fm
import os

# フォントパス設定
font_path = "./ipag.ttf"
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    matplotlib.rc('font', family=font_prop.get_name())
    print("日本語フォントが設定されました！")
else:
    print("フォントファイルが見つかりません。")
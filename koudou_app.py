import os

font_path = "./ipag.ttf"
if os.path.isfile(font_path):
    print(f"フォントファイルが見つかりました: {font_path}")
else:
    print(f"フォントファイルが見つかりません: {font_path}")
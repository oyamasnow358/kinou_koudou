import matplotlib.font_manager as fm

# システムにインストールされているフォント一覧を取得
for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
    print(font)
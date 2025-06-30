# app.spec
block_cipher = None

a = Analysis(
    ['app.py'],  # 你的 Flask 主文件
    pathex=[],
    binaries=[],
    datas=[],  # 可以添加静态文件（如 templates/, static/）
    hiddenimports=['flask', 'yt_dlp', 'mutagen'],  # 确保所有依赖都被包含
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BilibiliWebUI',  # 生成的 .exe 文件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 压缩可执行文件
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台（方便调试）
)
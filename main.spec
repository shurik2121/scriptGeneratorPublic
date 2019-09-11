# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:/ins/Mega/Dev/scriptGenerator/main.py'],
             pathex=['C:\\ins\\Mega\\Dev\\scriptGenerator'],
             binaries=[],
             datas=[('C:/ins/Mega/Dev/scriptGenerator/CSS', 'CSS/'), ('C:/ins/Mega/Dev/scriptGenerator/ui', 'ui/'), ('C:/ins/Mega/Dev/scriptGenerator/log', 'log/'), ('C:/ins/Mega/Dev/scriptGenerator/img', 'img/'), ('C:/ins/Mega/Dev/scriptGenerator/ini', 'ini/'), ('C:/ins/Mega/Dev/scriptGenerator/scripts', 'scripts/'), ('C:/ins/Mega/Dev/scriptGenerator/pdf', 'pdf/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='C:\\ins\\Mega\\Dev\\scriptGenerator\\img\\unload.ico', version='version.rc')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')

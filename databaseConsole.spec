# -*- mode: python -*-

block_cipher = None


a = Analysis(['databaseConsole.py'],
             pathex=['C:\\Users\\Ian\\Desktop\\EscapeGame'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.datas += [('Webster_Notes.png','C:\\Users\\Ian\\Desktop\\EscapeGame\\Webster_Notes.png', 'Data')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='databaseConsole',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

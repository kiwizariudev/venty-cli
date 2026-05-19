# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('docs', 'docs'),
        ('config/themes.json', 'config'),
        ('config/keybinds.json', 'config'),
    ],
    hiddenimports=[
        'actions', 'actions.files', 'actions.network', 'actions.browser',
        'actions.web', 'actions.control', 'actions.process', 'actions.compile',
        'actions.git', 'actions.system', 'actions.power', 'actions.windows',
        'actions.registry', 'actions.clipboard', 'actions.encode',
        'core', 'core.agent', 'core.config', 'core.executor', 'core.tasks',
        'core.prompt', 'core.jsonutil', 'core.memory', 'core.paths',
        'core.scheduler', 'core.logger', 'core.history', 'core.aliases',
        'core.context', 'ui', 'ui.colors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

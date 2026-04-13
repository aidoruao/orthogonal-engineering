# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Kingdom OS binary.

Bundles: kingdom_os_entry.py + oe_engine/ + kernel/ + axioms/ + src/ + ontology/
Output: single-file executable 'kingdom-os' (Linux) or 'kingdom-os.exe' (Windows)
"""

import os
import glob

block_cipher = None

# Collect all domain invariants, ontology JSON, and SAL modules
datas = [
    ('ontology/ontology.json', 'ontology'),
    ('src/domains', 'src/domains'),
    ('axioms', 'axioms'),
    ('src/sal', 'src/sal'),
    ('kernel', 'kernel'),
    ('oe_engine', 'oe_engine'),
]

a = Analysis(
    ['kingdom_os_entry.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'axioms.logic',
        'axioms.capability_security',
        'axioms.process_algebra',
        'kernel.boot',
        'kernel.scheduler',
        'kernel.memory_manager',
        'kernel.ipc',
        'kernel.anti_mimicry',
        'kernel.hal',
        'oe_engine.engine',
        'oe_engine.manifest',
        'oe_engine.router',
        'oe_engine.thinker',
        'oe_engine.speaker',
        'oe_engine.synthesizer',
        'oe_engine.generator',
        'oe_engine.conversation',
        'oe_engine.cli',
        'src.sal.cross_domain_adjunction',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'numpy', 'scipy', 'pandas', 'matplotlib', 'sklearn',
              'seaborn', 'tqdm', 'requests', 'lxml', 'ijson', 'cryptography'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='kingdom-os',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
)

# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Kingdom OS binary.

Bundles: kingdom_os_entry.py + oe_engine/ + kernel/ + axioms/ + src/ + ontology/
Output: single-file executable 'kingdom-os' (Linux) or 'kingdom-os.exe' (Windows)
"""

import os
import glob

# Collect all domain invariants, ontology JSON, and SAL modules
datas = [
    ('ontology/ontology.json', 'ontology'),
    ('src/domains', 'src/domains'),
    ('axioms', 'axioms'),
    ('src/sal', 'src/sal'),
    ('kernel', 'kernel'),
    ('oe_engine', 'oe_engine'),
]

# Auto-generate hiddenimports for all domain modules.
# thinker.py uses importlib.import_module() dynamically, so PyInstaller
# cannot trace these imports automatically — they must be listed explicitly.
_domain_hidden_imports = []
for _inv in sorted(glob.glob("src/domains/*/invariants.py")):
    # e.g. "src/domains/d_aerospace/invariants.py" -> "src.domains.d_aerospace.invariants"
    _mod = _inv.replace(os.sep, ".").replace("/", ".").removesuffix(".py")
    _domain_hidden_imports.append(_mod)
    # Also include the domain package itself and implementation module
    _pkg = _mod.rsplit(".", 1)[0]  # e.g. "src.domains.d_aerospace"
    _domain_hidden_imports.append(_pkg)
    _impl_path = _inv.replace("invariants.py", "implementation.py")
    if os.path.exists(_impl_path):
        _domain_hidden_imports.append(_pkg + ".implementation")
    _domain_path = _inv.replace("invariants.py", "domain.py")
    if os.path.exists(_domain_path):
        _domain_hidden_imports.append(_pkg + ".domain")

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
        *_domain_hidden_imports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'numpy', 'scipy', 'pandas', 'matplotlib', 'sklearn',
              'seaborn', 'tqdm', 'requests', 'lxml', 'ijson', 'cryptography'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

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

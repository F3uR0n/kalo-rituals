# PyInstaller hook for the locally-vendored OpenGL (PyOpenGL) package.
# Placed in project root; referenced by hookspath=['.'] in kalo_rituals.spec.
#
# PyOpenGL's plugin architecture registers array handlers and platform backends
# via string names at runtime — static analysis in the spec alone is not enough.
# This hook forces inclusion of all critical subpackages.

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('OpenGL')

datas = collect_data_files('OpenGL', include_py_files=False)

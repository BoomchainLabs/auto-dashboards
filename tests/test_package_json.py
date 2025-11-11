"""
Auto-generated tests for package.json
Framework: pytest
Focus: Validate schema and critical fields from the PR diff for package.json.
"""
import json
import re
from pathlib import Path

def load_pkg():
    return json.loads(Path("package.json").read_text(encoding="utf-8"))

def test_basic_metadata():
    pkg = load_pkg()
    assert pkg["name"] == "@orbrx/auto-dashboards"  # noqa: S101
    assert isinstance(pkg.get("version"), str)  # noqa: S101
    assert re.match(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$", pkg["version"])  # noqa: S101
    assert pkg.get("license") == "Apache-2.0"  # noqa: S101
    assert pkg.get("author", {}).get("name") == "Orange Bricks"  # noqa: S101

def test_entry_points_and_styles():
    pkg = load_pkg()
    assert pkg.get("main") == "lib/index.js"  # noqa: S101
    assert pkg.get("types") == "lib/index.d.ts"  # noqa: S101
    assert pkg.get("style") == "style/index.css"  # noqa: S101
    assert pkg.get("styleModule") == "style/index.js"  # noqa: S101

def test_files_globs_include_lib_and_style():
    pkg = load_pkg()
    files = " ".join(pkg.get("files", []))
    assert re.search(r"lib/\*\*/\*\.\{[^}]*js[^}]*\}", files)  # noqa: S101
    assert re.search(r"style/\*\*/\*\.\{[^}]*css[^}]*\}", files)  # noqa: S101

def test_scripts_include_critical_commands():
    pkg = load_pkg()
    s = pkg.get("scripts", {})
    for k in [
        "build",
        "build:lib",
        "build:labextension",
        "build:labextension:dev",
        "build:prod",
        "clean:lib",
        "install:extension",
    ]:
        assert k in s and isinstance(s[k], str) and len(s[k]) > 0  # noqa: S101

def test_jupyterlab_extension_configuration():
    pkg = load_pkg()
    jl = pkg.get("jupyterlab")
    assert jl and jl.get("extension") is True  # noqa: S101
    assert jl.get("outputDir") == "auto_dashboards/labextension"  # noqa: S101
    server = jl.get("discovery", {}).get("server", {})
    assert "pip" in server.get("managers", [])  # noqa: S101
    assert server.get("base", {}).get("name") == "auto_dashboards"  # noqa: S101

def test_publish_and_repository_fields():
    pkg = load_pkg()
    assert pkg.get("publishConfig", {}).get("access") == "public"  # noqa: S101
    assert re.search(r"github\.com/orbrx/auto-dashboards(\.git)?$", pkg.get("repository", {}).get("url", ""))  # noqa: S101
    assert re.search(r"github\.com/orbrx/auto-dashboards", pkg.get("homepage", ""))  # noqa: S101
    assert re.search(r"github\.com/orbrx/auto-dashboards/issues", pkg.get("bugs", {}).get("url", ""))  # noqa: S101

def test_side_effects_include_style_assets():
    pkg = load_pkg()
    se = pkg.get("sideEffects", [])
    assert "style/*.css" in se and "style/index.js" in se  # noqa: S101

def test_required_dependencies_and_ranges():
    pkg = load_pkg()
    deps = pkg.get("dependencies", {})
    for name in [
        "@jupyterlab/application",
        "@jupyterlab/apputils",
        "@jupyterlab/coreutils",
        "@jupyterlab/docregistry",
        "@jupyterlab/filebrowser",
        "@jupyterlab/fileeditor",
        "@jupyterlab/services",
        "@jupyterlab/ui-components",
        "@lumino/algorithm",
        "@lumino/commands",
        "@lumino/disposable",
    ]:
        assert name in deps and isinstance(deps[name], str) and re.match(r"^[\^~]\d+\.\d+\.\d+", deps[name])  # noqa: S101

def test_devdeps_typescript_has_compatible_range():
    pkg = load_pkg()
    ts = pkg.get("devDependencies", {}).get("typescript")
    assert isinstance(ts, str) and re.match(r"^[\^~]\d+\.\d+\.\d+", ts)  # noqa: S101

def test_jupyter_releaser_hooks():
    pkg = load_pkg()
    hooks = pkg.get("jupyter-releaser", {}).get("hooks", {})
    before_npm = hooks.get("before-build-npm", [])
    assert re.search(r"python -m pip install jupyterlab~=?4\.1", " ".join(before_npm))  # noqa: S101
    assert "jlpm" in before_npm  # noqa: S101
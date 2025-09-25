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
    assert pkg["name"] == "@orbrx/auto-dashboards"
    assert isinstance(pkg.get("version"), str)
    assert re.match(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$", pkg["version"])
    assert pkg.get("license") == "Apache-2.0"
    assert pkg.get("author", {}).get("name") == "Orange Bricks"


def test_entry_points_and_styles():
    pkg = load_pkg()
    assert pkg.get("main") == "lib/index.js"
    assert pkg.get("types") == "lib/index.d.ts"
    assert pkg.get("style") == "style/index.css"
    assert pkg.get("styleModule") == "style/index.js"


def test_files_globs_include_lib_and_style():
    pkg = load_pkg()
    files = " ".join(pkg.get("files", []))
    assert re.search(r"lib/\*\*/\*\.\{[^}]*js[^}]*\}", files)
    assert re.search(r"style/\*\*/\*\.\{[^}]*css[^}]*\}", files)


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
        assert k in s and isinstance(s[k], str) and len(s[k]) > 0


def test_jupyterlab_extension_configuration():
    pkg = load_pkg()
    jl = pkg.get("jupyterlab")
    assert jl and jl.get("extension") is True
    assert jl.get("outputDir") == "auto_dashboards/labextension"
    server = jl.get("discovery", {}).get("server", {})
    assert "pip" in server.get("managers", [])
    assert server.get("base", {}).get("name") == "auto_dashboards"


def test_publish_and_repository_fields():
    pkg = load_pkg()
    assert pkg.get("publishConfig", {}).get("access") == "public"
    assert re.search(r"github\.com/orbrx/auto-dashboards(\.git)?$", pkg.get("repository", {}).get("url", ""))
    assert re.search(r"github\.com/orbrx/auto-dashboards", pkg.get("homepage", ""))
    assert re.search(r"github\.com/orbrx/auto-dashboards/issues", pkg.get("bugs", {}).get("url", ""))


def test_side_effects_include_style_assets():
    pkg = load_pkg()
    se = pkg.get("sideEffects", [])
    assert "style/*.css" in se and "style/index.js" in se


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
        assert name in deps and isinstance(deps[name], str) and re.match(r"^[\^~]\d+\.\d+\.\d+", deps[name])


def test_devdeps_typescript_has_compatible_range():
    pkg = load_pkg()
    ts = pkg.get("devDependencies", {}).get("typescript")
    assert isinstance(ts, str) and re.match(r"^[\^~]\d+\.\d+\.\d+", ts)


def test_jupyter_releaser_hooks():
    pkg = load_pkg()
    hooks = pkg.get("jupyter-releaser", {}).get("hooks", {})
    before_npm = hooks.get("before-build-npm", [])
    assert re.search(r"python -m pip install jupyterlab~=?4\.1", " ".join(before_npm))
    assert "jlpm" in before_npm


def test_cleaning_scripts_chain_expected_commands():
    pkg = load_pkg()
    scripts = pkg.get("scripts", {})
    assert scripts.get("clean") == "jlpm clean:lib"
    assert scripts.get("clean:all") == "jlpm clean:lib && jlpm clean:labextension && jlpm clean:lintcache"
    assert scripts.get("clean:labextension") == "rimraf auto_dashboards/labextension"
    assert scripts.get("clean:lintcache") == "rimraf .eslintcache .stylelintcache"


def test_linting_and_formatting_scripts_alignment():
    pkg = load_pkg()
    scripts = pkg.get("scripts", {})
    assert scripts.get("lint") == "jlpm stylelint && jlpm prettier && jlpm eslint"
    assert scripts.get("lint:check") == "jlpm stylelint:check && jlpm prettier:check && jlpm eslint:check"
    assert scripts.get("prettier:base") == 'prettier "**/*{.ts,.tsx,.js,.jsx,.css,.json,.md}"'
    assert scripts.get("stylelint:check") == 'stylelint --cache "style/**/*.css"'


def test_watch_scripts_reference_expected_tooling():
    pkg = load_pkg()
    scripts = pkg.get("scripts", {})
    assert scripts.get("watch") == "run-p watch:src watch:labextension"
    assert scripts.get("watch:src") == "tsc -w"
    assert scripts.get("watch:labextension") == "jupyter labextension watch ."


def test_dev_dependencies_cover_tooling_versions():
    pkg = load_pkg()
    dev_deps = pkg.get("devDependencies", {})
    for name in [
        "@jupyterlab/builder",
        "@typescript-eslint/eslint-plugin",
        "@typescript-eslint/parser",
        "eslint",
        "prettier",
        "stylelint",
        "typescript",
    ]:
        assert name in dev_deps and isinstance(dev_deps[name], str) and len(dev_deps[name]) > 0
    assert dev_deps["typescript"].startswith("~5.")
    assert dev_deps["@jupyterlab/builder"].startswith("^4.")
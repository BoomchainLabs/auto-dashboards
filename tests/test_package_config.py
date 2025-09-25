import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = PROJECT_ROOT / "package.json"

@pytest.fixture(scope="module")
def package_json():
    data = json.loads(PACKAGE_JSON_PATH.read_text(encoding="utf-8"))
    return data

def test_package_metadata_basic(package_json):
    assert package_json["name"] == "@orbrx/auto-dashboards"
    assert package_json["version"] == "0.3.0"

def test_scripts_contain_required_entries(package_json):
    scripts = package_json["scripts"]
    assert scripts["build"] == "jlpm build:lib && jlpm build:labextension:dev"
    assert scripts["lint:check"] == "jlpm stylelint:check && jlpm prettier:check && jlpm eslint:check"

def test_dependencies_versions(package_json):
    deps = package_json["dependencies"]
    for key in (
        "@jupyterlab/application",
        "@jupyterlab/apputils",
        "@jupyterlab/coreutils",
        "@jupyterlab/docregistry",
        "@jupyterlab/filebrowser",
        "@jupyterlab/fileeditor",
        "@jupyterlab/services",
        "@jupyterlab/ui-components",
    ):
        assert key in deps
        assert deps[key].startswith("^4.") or deps[key].startswith("^7.")

def test_side_effects_and_style_module(package_json):
    side_effects = package_json["sideEffects"]
    assert "style/*.css" in side_effects
    assert "style/index.js" in side_effects
    assert package_json["styleModule"] == "style/index.js"

def test_jupyterlab_discovery_config(package_json):
    jupyter_config = package_json["jupyterlab"]["discovery"]
    server = jupyter_config["server"]
    assert server["managers"] == ["pip"]
    base = server["base"]
    assert base["name"] == "auto_dashboards"

def test_jupyter_releaser_hooks(package_json):
    hooks = package_json["jupyter-releaser"]["hooks"]
    assert hooks["before-build-npm"] == [
        "python -m pip install jupyterlab~=4.1",
        "jlpm",
    ]
    assert hooks["before-build-python"] == ["jlpm clean:all"]
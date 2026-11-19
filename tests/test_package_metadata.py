"""Regeneration must not silently discard declared runtime requirements."""

from pathlib import Path
import tomllib

from packaging.requirements import Requirement
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_distribution_preserves_the_declared_fern_requirements():
    config = yaml.safe_load((ROOT / "fern/sdk-config.yml").read_text())
    target = config["targets"][0]
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["name"] == target["package"]["packageName"]
    assert project["description"] == target["package"]["description"]
    assert project["requires-python"] == target["generation"]["pythonVersion"]
    dependencies = {
        Requirement(value).name: Requirement(value) for value in project["dependencies"]
    }
    for dependency in target["package"]["extraDependencies"]:
        if not dependency.get("optional"):
            assert str(dependencies[dependency["name"]].specifier) == str(
                Requirement(dependency["name"] + dependency["version"]).specifier
            )
    for extra, names in target["generation"]["extras"].items():
        actual = {
            Requirement(value).name: Requirement(value)
            for value in project["optional-dependencies"][extra]
        }
        assert set(actual) == set(names)
        for name in names:
            declared = next(
                d for d in target["package"]["extraDependencies"] if d["name"] == name
            )
            assert str(actual[name].specifier) == str(
                Requirement(name + declared["version"]).specifier
            )


def test_published_readme_describes_the_public_entry_point():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    readme = (ROOT / project["readme"]).read_text()
    assert "from harbor_client import HarborAPIClient" in readme
    assert "with HarborAPIClient(" in readme

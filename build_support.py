"""Build static exports from Fern's lazy model registry for wheel consumers."""
import ast
from pathlib import Path
from setuptools.command.build_py import build_py

def generate_export_stubs(directory: Path) -> None:
    """Expose lazy runtime model exports to static type checkers."""
    registry = ast.parse((directory / "types/__init__.py").read_text())
    mapping = next(
        (
            ast.literal_eval(node.value)
            for node in registry.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "_MODEL_TO_MODULE"
                for target in node.targets
            )
        ),
        None,
    )
    if not isinstance(mapping, dict) or not all(
        isinstance(name, str)
        and name.isidentifier()
        and isinstance(module, str)
        and all(part.isidentifier() for part in module.split("."))
        for name, module in mapping.items()
    ):
        raise SystemExit("The generated SDK has no valid lazy model export registry")
    header = "# Generated from the SDK's lazy export registry; do not edit.\n\n"
    (directory / "types/__init__.pyi").write_text(
        header
        + "".join(
            f"from .{module} import {name} as {name}\n"
            for name, module in sorted(mapping.items())
        )
    )
    exports = []
    public = set()
    for node in ast.parse((directory / "__init__.py").read_text()).body:
        if isinstance(node, ast.ImportFrom):
            for item in node.names:
                alias = item.asname or item.name
                if alias.startswith("_") and alias != "__version__":
                    continue
                exports.append(
                    f"from {'.' * node.level}{node.module or ''} import {item.name} as {alias}\n"
                )
                public.add(alias)
    exports.extend(
        f"from .types import {name} as {name}\n"
        for name in sorted(mapping)
        if name not in public
    )
    (directory / "__init__.pyi").write_text(header + "".join(exports))

class TypedBuildPy(build_py):
    def run(self):
        super().run()
        generate_export_stubs(Path(self.build_lib) / "harbor_client")

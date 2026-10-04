#!/usr/bin/env python3
"""Generate the checked-in function/library dependency map from repository source.

The script is intentionally lightweight.  It uses Python's standard `ast` module so
an engineer can regenerate the map without installing another static-analysis tool.
The output is documentation, not a call-graph proof: dynamic dispatch, reflection,
and runtime imports can only be represented when they are visible in source.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

# Resolve the repository root from this script instead of depending on the current
# working directory.  This keeps regeneration deterministic from an IDE or shell.
ROOT = Path(__file__).resolve().parents[1]
# Keep the generated document in the same place engineers look for architecture notes.
OUTPUT = ROOT / "docs" / "FUNCTION_LIBRARY_MAP.md"


def python_sources() -> list[Path]:
    """Return production Python modules in stable name order, excluding tests and tools."""
    # Restrict the dependency map to runtime modules; tests have a different change-impact role.
    return sorted(
        path
        for path in ROOT.glob("*.py")
        if not path.name.startswith("test_")
    )


def import_roots(tree: ast.AST) -> set[str]:
    """Return top-level imported module names visible in one parsed source file."""
    # A set prevents repeated imports from making a library appear more important than it is.
    roots: set[str] = set()
    # Walk every syntax node because imports can legally appear inside functions.
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # `import a.b` is mapped to library root `a` for change-impact purposes.
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            # `from a.b import c` has the same top-level dependency root `a`.
            roots.add(node.module.split(".", 1)[0])
    return roots


def dotted_call_name(node: ast.Call) -> str | None:
    """Return a readable dotted call target when a call is statically identifiable."""
    # A direct function call such as `ppm(...)` is represented by an AST Name.
    if isinstance(node.func, ast.Name):
        return node.func.id
    # Method/module calls such as `np.asarray(...)` are represented by nested Attributes.
    if isinstance(node.func, ast.Attribute):
        parts: list[str] = [node.func.attr]
        value = node.func.value
        # Walk backward through `a.b.c` until the root identifier is reached.
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
            return ".".join(reversed(parts))
    # Dynamic call targets cannot be mapped reliably without executing the program.
    return None


def iter_functions(tree: ast.AST) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Yield every function definition, including methods and nested helpers."""
    # `ast.walk` includes nested functions, which matter because they can hold numerical logic.
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def first_line_doc(node: ast.AST) -> str:
    """Return the first docstring line for a mapped function or class."""
    # The source standard requires docstrings; a fallback keeps the generator robust during edits.
    doc = ast.get_docstring(node) or "Documentation required."
    return doc.strip().splitlines()[0]


def generate() -> str:
    """Build the complete Markdown dependency map from the current repository source."""
    # Parse every runtime module first so cross-module local function names can be recognized.
    parsed: dict[str, ast.Module] = {}
    functions_by_module: dict[str, list[ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    local_names: set[str] = set()
    for source in python_sources():
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        parsed[source.name] = tree
        functions = sorted(iter_functions(tree), key=lambda item: item.lineno)
        functions_by_module[source.name] = functions
        local_names.update(node.name for node in functions)

    # Build a lightweight reverse call index.  Python permits dynamic dispatch,
    # so this is intentionally documented as a static change-impact aid rather
    # than a formal whole-program call graph.
    reverse_callers: dict[str, set[str]] = {name: set() for name in local_names}
    for module_name, functions in functions_by_module.items():
        for node in functions:
            caller_name = f"{module_name}:{node.name}"
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                call_name = dotted_call_name(child)
                if not call_name:
                    continue
                target_name = call_name.split(".")[-1]
                if target_name in reverse_callers and target_name != node.name:
                    reverse_callers[target_name].add(caller_name)

    # Start with an engineering explanation of what the static map can and cannot tell us.
    lines = [
        "# Function / Library Dependency Map",
        "",
        "This file is generated from the current Python source by `tools/generate_function_map.py`.",
        "It is a change-impact aid: it shows module libraries, statically visible project calls, and direct project callers so an engineer can identify likely affected code before modifying a calculation or interface.",
        "",
        "> Dynamic dispatch, callbacks, subprocess boundaries, and runtime imports may not appear as direct calls. Use this map together with regression tests and code review.",
        "",
    ]

    # Emit one section per runtime module so the document mirrors the repository layout.
    for module_name in sorted(parsed):
        tree = parsed[module_name]
        dependencies = sorted(import_roots(tree))
        local_deps = sorted(name for name in dependencies if name.startswith("cdcu_") or name == "magnet_load_diagnostics")
        external_deps = sorted(name for name in dependencies if name not in local_deps and name != "__future__")
        lines.extend(
            [
                f"## `{module_name}`",
                "",
                f"**Project-module dependencies:** {', '.join(f'`{name}`' for name in local_deps) if local_deps else 'None'}",
                "",
                f"**Python / third-party libraries:** {', '.join(f'`{name}`' for name in external_deps) if external_deps else 'None'}",
                "",
                "| Function | Purpose | Calls project functions | Direct project callers | External/library calls (selected) |",
                "| --- | --- | --- | --- | --- |",
            ]
        )

        # Map each function independently so a small code change has a small review surface.
        for node in functions_by_module[module_name]:
            call_names = [
                name
                for child in ast.walk(node)
                if isinstance(child, ast.Call)
                for name in [dotted_call_name(child)]
                if name
            ]
            project_calls = sorted(
                {
                    name
                    for name in call_names
                    if name.split(".")[-1] in local_names and name.split(".")[-1] != node.name
                }
            )
            callers = sorted(reverse_callers.get(node.name, set()))
            external_calls = sorted({name for name in call_names if name not in project_calls and "." in name})
            # Limit verbose columns so the map remains usable in GitHub rendering.
            displayed_callers = callers[:10]
            if len(callers) > 10:
                displayed_callers.append("…")
            displayed_external = external_calls[:12]
            if len(external_calls) > 12:
                displayed_external.append("…")
            lines.append(
                "| "
                + f"`{node.name}` | {first_line_doc(node).replace('|', '\\|')} | "
                + (", ".join(f"`{name}`" for name in project_calls) if project_calls else "—")
                + " | "
                + (", ".join(f"`{name}`" for name in displayed_callers) if displayed_callers else "—")
                + " | "
                + (", ".join(f"`{name}`" for name in displayed_external) if displayed_external else "—")
                + " |"
            )
        lines.append("")

    # Add a short review checklist so the map is used as a maintenance tool, not passive documentation.
    lines.extend(
        [
            "## Change-impact checklist",
            "",
            "When a function changes, review its project callees, direct callers, module-level dependencies, and corresponding regression tests. If a result dictionary or CSV schema changes, update the AI data contract and report readers in the same change.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    """Regenerate `docs/FUNCTION_LIBRARY_MAP.md` and return zero on success."""
    # Create the documentation directory in case the repository was freshly cloned.
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    # Write UTF-8 Markdown so symbols and engineering notation survive across platforms.
    OUTPUT.write_text(generate(), encoding="utf-8")
    # Print the path as a simple confirmation for local development and CI logs.
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    # Convert the function return code into the process exit status expected by shell tooling.
    raise SystemExit(main())

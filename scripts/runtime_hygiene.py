from __future__ import annotations

import ast
from pathlib import Path


TEST_ONLY_ROOTS = {"pytest", "unittest", "hypothesis"}


def violations(root: Path) -> list[str]:
    problems: list[str] = []
    for path in sorted((root / "src").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".", 1)[0] in TEST_ONLY_ROOTS:
                        problems.append(
                            f"{path}: production source imports test-only package {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.split(".", 1)[0] in TEST_ONLY_ROOTS:
                    problems.append(
                        f"{path}: production source imports test-only package {module}"
                    )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    problems.append(
                        f"{path}:{node.lineno}: production source defines test function {node.name}"
                    )
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("Test"):
                    problems.append(
                        f"{path}:{node.lineno}: production source defines test class {node.name}"
                    )
    return problems


def main() -> int:
    problems = violations(Path("."))
    if problems:
        print("Runtime hygiene violations:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Runtime hygiene: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

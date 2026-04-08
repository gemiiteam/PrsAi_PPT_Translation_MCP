import ast
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    server_py = repo_root / "src" / "prs_ai_staging_mcp" / "server.py"
    main_py = repo_root / "src" / "prs_ai_staging_mcp" / "__main__.py"

    ast.parse(server_py.read_text(encoding="utf-8"))
    ast.parse(main_py.read_text(encoding="utf-8"))
    print("ok")


if __name__ == "__main__":
    main()


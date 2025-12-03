import os

PROJECT_ROOT = "equity-fundamentals-analytics"

FOLDERS = [
    "data/raw",
    "data/clean",
    "data/feature",
    "data/analytics",
    "notebooks/intake",
    "notebooks/cleaning",
    "notebooks/features",
    "notebooks/analytics",
    "src/equity_analytics/config",
    "tests",
    "docs",
]

FILES = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "LICENSE",
    "src/equity_analytics/__init__.py",
    "docs/architecture.md",
    "docs/workflow.md",
    "docs/metrics_dictionary.md",
    "docs/project_tracker.md",
]


def create_folder(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def create_file(path: str) -> None:
    if not os.path.exists(path):
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("")


def main() -> None:
    # 1) Create project root
    create_folder(PROJECT_ROOT)

    # 2) Go inside project root
    os.chdir(PROJECT_ROOT)

    # 3) Create folders
    for folder in FOLDERS:
        create_folder(folder)

    # 4) Create files
    for file in FILES:
        create_file(file)

    print(f"✅ Project structure created at ./{PROJECT_ROOT}")


if __name__ == "__main__":
    main()
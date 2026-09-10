import os

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".go": "go",
}
SUPPORTED_EXTENSIONS = tuple(LANGUAGE_MAP.keys())


def load_repository(file_path):
    source_files = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith(SUPPORTED_EXTENSIONS):
                full_path = os.path.join(root, file)
                source_files.append(full_path)
    return source_files


def read_file(file_path):
    extension = os.path.splitext(file_path)[1]
    language = LANGUAGE_MAP.get(extension)
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            return {
                "content": file_content,
                "metadata": {
                    "file_path": file_path,
                    "extension": extension,
                    "language": language,
                    "file_name": file_name,
                },
            }
    except UnicodeDecodeError:
        return None

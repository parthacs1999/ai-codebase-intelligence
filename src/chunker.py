
from tree_sitter_language_pack import get_parser


STRUCTURAL_NODES = {
    "python": {
        "function_definition": "function",
        "class_definition": "class",
    },
    "javascript": {
        "function_declaration": "function",
        "class_declaration": "class",
        "method_definition": "method",
    },
    "typescript": {
        "function_declaration": "function",
        "class_declaration": "class",
        "method_definition": "method",
    },
    "java": {
        "class_declaration": "class",
        "method_declaration": "method",
        "constructor_declaration": "constructor",
    },
    "cpp": {
        "function_definition": "function",
        "class_specifier": "class",
    },
    "go": {
        "function_declaration": "function",
        "method_declaration": "method",
    },
}


def chunk_structured_code(document):
    content = document["content"]
    metadata = document["metadata"]
    language = metadata["language"]

    if language not in STRUCTURAL_NODES:
        return None

    parser = get_parser(language)
    code_bytes = content.encode("utf-8")
    tree = parser.parse(code_bytes)

    chunks = [
        {
            "content": content,
            "metadata": {
                **metadata,
                "chunk_type": "file",
                "symbol_name": metadata["file_name"],
                "qualified_name": metadata["file_name"],
                "start_line": 1,
                "end_line": len(content.splitlines()),
            },
        }
    ]

    def traverse(node, parent_symbol=None, parent_type=None):
        next_parent = parent_symbol
        next_parent_type = parent_type

        if node.type in STRUCTURAL_NODES[language]:
            chunk_type = STRUCTURAL_NODES[language][node.type]
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                symbol_name = code_bytes[
                    name_node.start_byte:name_node.end_byte
                ].decode("utf-8")
            else:
                symbol_name = "unknown"

            if parent_symbol and symbol_name != "unknown":
                qualified_name = f"{parent_symbol}.{symbol_name}"
            else:
                qualified_name = symbol_name

            if language == "python" and chunk_type == "function":
                if parent_type == "class":
                    chunk_type = "method"

            chunk_text = code_bytes[
                node.start_byte:node.end_byte
            ].decode("utf-8")

            chunks.append(
                {
                    "content": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_type": chunk_type,
                        "symbol_name": symbol_name,
                        "qualified_name": qualified_name,
                        "start_line": int(node.start_point[0]) + 1,
                        "end_line": int(node.end_point[0]) + 1,
                    },
                }
            )

            if symbol_name != "unknown":
                next_parent = qualified_name
                next_parent_type = chunk_type

        for child in node.children:
            traverse(child, next_parent, next_parent_type)

    traverse(tree.root_node)

    for index, chunk in enumerate(chunks):
        chunk["metadata"]["chunk_index"] = index

    return chunks


def chunk_code(document, chunk_size=5, overlap=2):
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    content = document["content"]
    document_metadata = document["metadata"]
    lines = content.splitlines()

    step = chunk_size - overlap
    chunks = []
    chunk_ind = 0

    for ind in range(0, len(lines), step):
        chunk_lines = lines[ind:ind + chunk_size]
        chunk_text = "\n".join(chunk_lines)

        chunk_data = {
            "content": chunk_text,
            "metadata": {
                **document_metadata,
                "chunk_index": chunk_ind,
                "chunk_type": "line",
                "symbol_name": "",
                "qualified_name": "",
                "start_line": ind + 1,
                "end_line": min(ind + chunk_size, len(lines)),
            },
        }

        chunks.append(chunk_data)
        chunk_ind += 1

        if ind + chunk_size >= len(lines):
            break

    return chunks


def smart_chunk_code(document, chunk_size=5, overlap=2):
    structural_chunks = chunk_structured_code(document)

    if structural_chunks:
        return structural_chunks

    return chunk_code(
        document,
        chunk_size=chunk_size,
        overlap=overlap,
    )


if __name__ == "__main__":
    from repository_loader import read_file

    document = read_file("sample_repo/backend/user.js")

    chunks = smart_chunk_code(document)

    for chunk in chunks:
        metadata = chunk["metadata"]

        print("\n--------------------")
        print("Index:", metadata["chunk_index"])
        print("Type:", metadata.get("chunk_type"))
        print("Name:", metadata.get("symbol_name"))
        print("Qualified Name:", metadata.get("qualified_name"))

        print(
            "Lines:",
            metadata["start_line"],
            "-",
            metadata["end_line"],
        )

        print("\nCode:")
        print(chunk["content"])

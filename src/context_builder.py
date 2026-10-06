def build_context(results):
    context_parts = []

    for i, result in enumerate(results, start=1):
        content = result["content"]
        metadata = result["metadata"]

        chunk_type = metadata.get("chunk_type", "Unknown")
        file_path = metadata["file_path"]
        symbol_name = metadata.get("symbol_name", "Unknown")
        start_line = metadata["start_line"]
        end_line = metadata["end_line"]

        source = f"""[Source {i}]
File: {file_path}
Type: {chunk_type}
Symbol: {symbol_name}
Lines: {start_line}-{end_line}

Code:
{content}"""

        context_parts.append(source)

    return "\n\n".join(context_parts)

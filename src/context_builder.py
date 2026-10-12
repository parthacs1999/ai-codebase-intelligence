
def build_context(results):
    context_parts = []

    for index, result in enumerate(results, start=1):
        content = result["content"]
        metadata = result["metadata"]

        file_path = metadata.get("file_path", "Unknown")
        chunk_type = metadata.get("chunk_type", "Unknown")
        symbol_name = metadata.get("symbol_name", "Unknown")
        qualified_name = metadata.get("qualified_name", "")
        start_line = metadata.get("start_line", "Unknown")
        end_line = metadata.get("end_line", "Unknown")

        source = (
            f"[Source {index}]\n"
            f"File: {file_path}\n"
            f"Type: {chunk_type}\n"
            f"Symbol: {symbol_name}\n"
            f"Qualified Symbol: {qualified_name}\n"
            f"Lines: {start_line}-{end_line}\n\n"
            f"Code:\n{content}"
        )

        context_parts.append(source)

    return "\n\n".join(context_parts)

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
        chunk_lines = lines[ind : ind + chunk_size]
        chunk_text = "\n".join(chunk_lines)
        chunk_data = {
            "content": chunk_text,
            "metadata": {
                **document_metadata,
                "chunk_index": chunk_ind,
                "start_line": ind + 1,
                "end_line": min(ind + chunk_size, len(lines)),
            },
        }
        chunk_ind = chunk_ind + 1
        chunks.append(chunk_data)
        if ind + chunk_size >= len(lines):
            break
    return chunks

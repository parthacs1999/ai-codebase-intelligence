
import re


CITATION_PATTERN = re.compile(
    r"\[Source\s+(\d+)\]",
    re.IGNORECASE
)


def extract_citations(answer):
    return [
        int(match)
        for match in CITATION_PATTERN.findall(answer)
    ]


def validate_citations(answer, results):
    citations = extract_citations(answer)

    valid_ids = set(
        range(1, len(results) + 1)
    )

    invalid_ids = sorted(
        set(citations) - valid_ids
    )

    cited_ids = sorted(
        set(citations) & valid_ids
    )

    uncited_ids = sorted(
        valid_ids - set(citations)
    )

    return {
        "valid": len(invalid_ids) == 0,
        "has_citations": len(citations) > 0,
        "citation_count": len(citations),
        "cited_sources": cited_ids,
        "invalid_sources": invalid_ids,
        "uncited_sources": uncited_ids
    }


def get_cited_source_details(answer, results):
    citations = extract_citations(answer)

    details = []
    seen = set()

    for citation_id in citations:
        if citation_id in seen:
            continue

        seen.add(citation_id)

        if not 1 <= citation_id <= len(results):
            continue

        metadata = results[citation_id - 1]["metadata"]

        details.append({
            "source_id": citation_id,
            "file_path": metadata.get(
                "file_path", "Unknown"
            ),
            "qualified_name": metadata.get(
                "qualified_name", ""
            ),
            "start_line": metadata.get(
                "start_line", "Unknown"
            ),
            "end_line": metadata.get(
                "end_line", "Unknown"
            )
        })

    return details

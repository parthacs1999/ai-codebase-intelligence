
from citation_validator import (
    validate_citations,
    get_cited_source_details
)


results = [
    {
        "content": "def verify_signature(): pass",
        "metadata": {
            "file_path": "signer.py",
            "qualified_name": "Signer.verify_signature",
            "start_line": 10,
            "end_line": 20
        }
    },
    {
        "content": "def unsign(): pass",
        "metadata": {
            "file_path": "signer.py",
            "qualified_name": "Signer.unsign",
            "start_line": 25,
            "end_line": 35
        }
    }
]


def main():
    answer = (
        "Signature verification happens in "
        "Signer.verify_signature [Source 1]. "
        "Unsigning is implemented in "
        "Signer.unsign [Source 2]."
    )

    validation = validate_citations(
        answer,
        results
    )

    details = get_cited_source_details(
        answer,
        results
    )

    print("Validation:", validation)
    print("Cited sources:", details)

    assert validation["valid"]
    assert validation["has_citations"]
    assert validation["cited_sources"] == [1, 2]

    invalid_answer = (
        "The implementation uses an unknown method "
        "[Source 99]."
    )

    invalid_validation = validate_citations(
        invalid_answer,
        results
    )

    assert not invalid_validation["valid"]
    assert invalid_validation["invalid_sources"] == [99]

    print("Citation tests passed")


if __name__ == "__main__":
    main()

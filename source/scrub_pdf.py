import sys
from pypdf import PdfReader, PdfWriter


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: scrub_pdf.py INPUT OUTPUT")
    reader = PdfReader(sys.argv[1])
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.add_metadata(
        {
            "/Title": "Xpert Technical Portfolio",
            "/Author": "",
            "/Creator": "Xpert Portfolio",
            "/Producer": "Xpert Portfolio",
            "/Subject": "ByteDance Xpert technical portfolio",
        }
    )
    with open(sys.argv[2], "wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    main()

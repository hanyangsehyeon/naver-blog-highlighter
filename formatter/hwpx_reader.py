import io
import zipfile
import xml.etree.ElementTree as ET


def read_hwpx_bytes(data: bytes) -> str:
    """Extract plain text from hwpx file bytes."""
    extracted = []
    with zipfile.ZipFile(io.BytesIO(data), "r") as z:
        section_files = sorted(
            f for f in z.namelist()
            if f.startswith("Contents/section") and f.endswith(".xml")
        )
        if not section_files:
            raise ValueError("section XML not found in hwpx file")
        for section_file in section_files:
            with z.open(section_file) as f:
                root = ET.fromstring(f.read())
                for tag in root.iter():
                    if tag.tag.endswith("}t") or tag.tag == "t":
                        if tag.text:
                            extracted.append(tag.text)
                    elif tag.tag.endswith("}p") or tag.tag == "p":
                        extracted.append("\n")
    return "".join(extracted).strip()

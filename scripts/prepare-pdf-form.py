"""Embed a complete OFL Chinese font in the XeLaTeX AcroForm for future input."""
from io import BytesIO
from dataclasses import replace
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject
from pypdf.generic._font import Font

ROOT = Path(__file__).resolve().parent.parent
LABELS = {
    'applicantName': '姓名', 'studentId': '学号', 'email': '邮箱',
    'invoiceCount': '发票张数', 'invoiceAmounts': '发票金额明细（元）',
    'totalAmount': '总金额（元）', 'explanation': '情况说明',
}


def prepare(source: Path, destination: Path) -> None:
    writer = PdfWriter(clone_from=source)
    form = writer.root_object['/AcroForm']
    resources = form.setdefault(NameObject('/DR'), DictionaryObject())
    fonts = resources.setdefault(NameObject('/Font'), DictionaryObject())
    # A subset of the printed labels cannot render arbitrary names/explanations.
    # Use pypdf/fontTools' TrueType embedding and Unicode mapping implementation.
    font = Font.from_truetype_font_file(BytesIO(
        (ROOT / 'latex/fonts/ResourceHanRoundedCN-Regular.ttf').read_bytes()
    ))
    font.font_descriptor = replace(
        font.font_descriptor, font_file=font.font_descriptor.font_file.flate_encode()
    )
    font._add_to_writer(writer, fonts, NameObject('/FormCJK'))
    default = TextStringObject('/FormCJK 12 Tf 0 g')
    form[NameObject('/DA')] = default
    for page in writer.pages:
        for reference in page.get('/Annots', []):
            widget = reference.get_object()
            if widget.get('/Subtype') == '/Widget':
                widget[NameObject('/DA')] = default
                # Store Unicode tooltips explicitly rather than TeX's PDF string escapes.
                widget[NameObject('/TU')] = TextStringObject(LABELS[widget['/T']])
    writer.update_page_form_field_values(
        None, {name: '' for name in writer.get_fields()}, auto_regenerate=False
    )
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    for page in writer.pages:
        page.compress_content_streams()
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer.write(destination)
    if len(PdfReader(destination).get_fields() or {}) != 7:
        raise ValueError('Expected seven interactive fields')
    print(f'Prepared fillable PDF: {destination.name}')


if __name__ == '__main__':
    prepare(Path(sys.argv[1]), Path(sys.argv[2]))

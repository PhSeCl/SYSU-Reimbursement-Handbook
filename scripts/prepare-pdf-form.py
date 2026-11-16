"""Embed Windows SimSun in the XeLaTeX AcroForm for Chinese and numeric input."""
from io import BytesIO
from dataclasses import replace
from pathlib import Path
import sys
import os

from fontTools.ttLib import TTFont
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject
from pypdf.generic._font import Font

ROOT = Path(__file__).resolve().parent.parent
LABELS = {
    'applicantName': '姓名', 'studentId': '学号', 'email': '邮箱',
    'invoiceCount': '发票张数', 'invoiceAmounts': '发票金额明细（元）',
    'totalAmount': '总金额（元）', 'explanation': '情况说明',
    'purpose': '事由', 'travelStartDate': '出差开始日期',
    'travelEndDate': '出差结束日期',
    'originCampus': '出发校区', 'destinationCampus': '出差校区',
    'roundTripCount': '往返次数', 'oneWayCount': '单程次数',
    'oneWayExplanation': '单程说明', 'otherExplanation': '其他说明',
}


def prepare(source: Path, destination: Path) -> None:
    writer = PdfWriter(clone_from=source)
    form = writer.root_object['/AcroForm']
    resources = form.setdefault(NameObject('/DR'), DictionaryObject())
    fonts = resources.setdefault(NameObject('/Font'), DictionaryObject())
    # A subset of the printed labels cannot render arbitrary names/explanations.
    # Use pypdf/fontTools' TrueType embedding and Unicode mapping implementation.
    # Extract SimSun (face 0) from the Windows collection in memory; do not
    # redistribute the system font as a source asset in the repository.
    system_font = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/simsun.ttc'
    with TTFont(system_font, fontNumber=0) as ttf:
        if ttf['OS/2'].fsType & 0x0002:
            raise ValueError('The installed SimSun font disallows embedding')
        data = BytesIO()
        ttf.save(data)
    data.seek(0)
    font = Font.from_truetype_font_file(data)
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
    # Keep each widget's appearance independent: pypdf updates saved appearances
    # in place, so deduplicating equal-size blank widgets couples later values.
    writer.compress_identical_objects(remove_duplicates=False, remove_unreferenced=True)
    for page in writer.pages:
        page.compress_content_streams()
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer.write(destination)
    expected = 15 if 'cross-campus' in destination.name else 7
    if len(PdfReader(destination).get_fields() or {}) != expected:
        raise ValueError(f'Expected {expected} interactive fields')
    print(f'Prepared fillable PDF: {destination.name}')


if __name__ == '__main__':
    prepare(Path(sys.argv[1]), Path(sys.argv[2]))

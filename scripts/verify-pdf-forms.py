"""Check blank forms and Chinese fill/save round trips, retaining QA copies in tmp."""
from pathlib import Path
import json
import re
import sys
import unicodedata

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

ROOT = Path(__file__).resolve().parent.parent
CENTERED_FIELDS = {
    'invoiceCount', 'totalAmount', 'travelStartDate', 'travelEndDate',
    'roundTripCount', 'oneWayCount',
}
COMMON_VALUES = {
    'applicantName': '测试队员',
    'studentId': '00000000',
    'email': 'sample@example.com',
    'invoiceCount': '5',
    'invoiceAmounts': '40 + 40 + 40 + 40 + 40\n五张发票，每张四十元。',
    'totalAmount': '200.00',
}
EXPLANATION = (
    '此处为表单显示测试，所填内容仅用于检查中文与换行。\n'
    '第一行：赴校区参加训练，申请报销实际发生的交通费用。\n'
    '第二行：逐项核对发票金额、行程及报销范围。\n'
    '第三行：中文标点、英文 ABC 和数字 123 均应完整显示。'
)
CROSS_CAMPUS_VALUES = {
    'purpose': '网球队跨校区训练交通费',
    'travelStartDate': '2026-09-01',
    'travelEndDate': '2026-09-30',
    'originCampus': '一二三四五六七八九十',
    'destinationCampus': '甲乙丙丁戊己庚辛壬癸',
    'roundTripCount': '2',
    'oneWayCount': '1',
    'oneWayExplanation': '第三次训练后随队赴赛场，仅申请前往南校园的单程校车费。',
    'otherExplanation': '南校园至赛场及赛场返回所在校区的费用归入比赛报销，本次不再申报。',
}


def inspect(path: Path, values: dict[str, str]) -> PdfReader:
    reader = PdfReader(path)
    assert len(reader.pages) == 1, f'{path.name}: expected one page'
    assert not reader.attachments, f'{path.name}: unexpected attachments'
    assert reader.metadata.author == 'PhSeCl'
    assert '/JavaScript' not in reader.root_object.get('/Names', {})
    fields = reader.get_fields() or {}
    assert set(fields) == set(values), f'{path.name}: unexpected field tree'
    for name, expected in values.items():
        assert fields[name].get('/V', '') == expected, f'{name}: canonical value mismatch'
        assert fields[name].get('/FT') == '/Tx', f'{name}: expected text field'
        assert not (int(fields[name].get('/Ff', 0)) & 1), f'{name}: read-only field'
    seen = set()
    canonical = {ref.idnum for ref in reader.root_object['/AcroForm']['/Fields']}
    for ref in reader.pages[0].get('/Annots', []):
        widget = ref.get_object()
        if widget.get('/Subtype') != '/Widget':
            continue
        # XeLaTeX produces merged field/widget objects; reject duplicate orphan trees.
        assert ref.idnum in canonical, 'Widget is disconnected from the canonical field tree'
        name = widget['/T']
        assert name not in seen, f'Duplicate widget: {name}'
        seen.add(name)
        assert widget.get('/Q', 0) == (1 if name in CENTERED_FIELDS else 0), f'{name}: alignment mismatch'
        assert widget.get('/V', '') == values[name], f'{name}: widget value mismatch'
        assert int(widget.get('/F', 0)) & 4, f'{name}: field will not print'
        assert widget['/AP']['/N'].get_data(), f'{name}: missing appearance'
        x0, y0, x1, y1 = widget['/Rect']
        assert 0 <= x0 < x1 <= reader.pages[0].mediabox.right
        assert 0 <= y0 < y1 <= reader.pages[0].mediabox.top
    assert seen == set(values), 'Missing interactive widgets'
    multiline = {'invoiceAmounts', 'explanation', 'oneWayExplanation', 'otherExplanation'} & values.keys()
    assert all(fields[name]['/Ff'] & 4096 for name in multiline)
    fonts = reader.root_object['/AcroForm']['/DR']['/Font']
    cjk = fonts['/FormCJK']
    assert cjk['/Subtype'] == '/Type0'
    assert cjk['/BaseFont'] == '/SimSun'
    assert len(cjk['/DescendantFonts'][0]['/FontDescriptor']['/FontFile2'].get_data()) > 1_000_000
    return reader


def verify(pdf_root: Path) -> None:
    qa_root = ROOT / 'tmp/pdf-form-qa'
    qa_root.mkdir(parents=True, exist_ok=True)
    results = []
    for name in ('reimbursement-summary', 'cross-campus-summary'):
        values = COMMON_VALUES | (CROSS_CAMPUS_VALUES if name == 'cross-campus-summary' else {'explanation': EXPLANATION})
        source = pdf_root / f'{name}-form.pdf'
        reader = inspect(source, dict.fromkeys(values, ''))
        # Use the same embedded font a viewer uses, and generate real saved appearances.
        writer = PdfWriter(clone_from=reader)
        writer.update_page_form_field_values(None, values, auto_regenerate=False)
        filled = qa_root / f'{name}-filled.pdf'
        writer.write(filled)
        reopened = inspect(filled, values)
        # Compare saved numeric baselines to their printed labels, in PDF points.
        labels = {}
        def capture(text, cm, tm, font, size):
            for field, label in (('invoiceCount', '发票张数：'), ('totalAmount', '总金额：'), ('roundTripCount', '往返次数：'), ('oneWayCount', '单程次数：'), ('travelStartDate', '出差日期：'), ('travelEndDate', '出差日期：'), ('originCampus', '出发校区：'), ('destinationCampus', '出差校区：')):
                if label in text:
                    labels[field] = tm[5] + cm[5]
        reopened.pages[0].extract_text(visitor_text=capture)
        # Extract each saved appearance separately: values alone do not prove visible text.
        for ref in reopened.pages[0]['/Annots']:
            widget = ref.get_object()
            if widget.get('/Subtype') != '/Widget':
                continue
            appearance = widget['/AP']['/N']
            probe = PdfWriter()
            page = probe.add_blank_page(width=600, height=850)
            page.replace_contents(appearance)
            page[NameObject('/Resources')] = appearance['/Resources']
            # pypdf normalizes compatibility punctuation in the embedded ToUnicode map.
            normalize = lambda text: re.sub(r'\s+', '', unicodedata.normalize('NFKC', text))
            assert normalize(page.extract_text()) == normalize(values[widget['/T']]), (
                f"{name}/{widget['/T']}: saved appearance text differs from field value"
            )
            field = widget['/T']
            if field in labels:
                positions = []
                page.extract_text(visitor_text=lambda text, cm, tm, font, size: positions.append(tm[5] + cm[5]) if text.strip() else None)
                assert positions, f'{field}: missing numeric appearance'
                delta = float(widget['/Rect'][1]) + positions[0] - labels[field]
                assert abs(delta) < 0.75, f'{name}/{field}: baseline differs by {delta:.3f}pt'
        # Flatten appearances as a print-equivalent QA copy, retaining no widgets.
        print_writer = PdfWriter(clone_from=reopened)
        print_writer.update_page_form_field_values(None, values, auto_regenerate=False, flatten=True)
        print_writer.remove_annotations(subtypes='/Widget')
        del print_writer.root_object[NameObject('/AcroForm')]
        printed = qa_root / f'{name}-print.pdf'
        print_writer.write(printed)
        printed_reader = PdfReader(printed)
        assert '/Annots' not in printed_reader.pages[0] or not printed_reader.pages[0]['/Annots']
        printed_text = printed_reader.pages[0].extract_text()
        for value in values.values():
            assert normalize(value) in normalize(printed_text), f'{name}: text lost in print copy'
        log_path = ROOT / f'tmp/latex-form-{name}/main.log'
        if log_path.exists():
            assert not re.search(r'Overfull \\[hv]box|Missing character:|undefined', log_path.read_text(encoding='utf8', errors='replace'))
        results.append({'file': source.name, 'pages': 1, 'editableFields': len(values), 'chineseRoundTrip': True, 'numericBaselinesAligned': True, 'printCopyChecked': True})
    (qa_root / 'pdf-audit.json').write_text(json.dumps(results, indent=2), encoding='utf8')
    print(json.dumps(results))


if __name__ == '__main__':
    verify(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'output/pdf')

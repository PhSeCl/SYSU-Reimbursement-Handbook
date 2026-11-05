"""Check the compiled LaTeX PDF before replacing the publication."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
build = ROOT / 'tmp/latex'
pdf = PdfReader(build / 'main.pdf')
log = (build / 'main.log').read_text(encoding='utf8', errors='replace')
for pattern in (r'Overfull \\[hv]box', r'Missing character:', r'LaTeX Warning:.*undefined', r'Font shape.*undefined', r'fontspec Warning:'):
    if re.search(pattern, log):
        raise ValueError(f'LaTeX diagnostic requires attention: {pattern}')
aux = (build / 'main.aux').read_text(encoding='utf8')
page_count = re.search(r'\\@abspage@last\{(\d+)\}', aux)
if not page_count or len(pdf.pages) != int(page_count[1]):
    raise ValueError('PDF page count differs from the current LaTeX build')
clean = lambda s: re.sub(r'\s+', '', s).replace('\u2011','-').replace('\u2010','-')
texts = [clean(p.extract_text()) for p in pdf.pages]
text = ''.join(texts)
if pdf.metadata.author != 'PhSeCl' or pdf.metadata.title != 'SYSU-Reimbursement-Handbook':
    raise ValueError('Publication metadata mismatch')
if 'xdvipdfmx' not in pdf.metadata.producer:
    raise ValueError('Publication was not produced by the XeLaTeX pipeline')
for value in ('中山大学','121000004558631445','广东省广州市新港西路135号','020-84110285','中国建设银行广州中山大学支行','44050143004609000001'):
    if value not in text:
        raise ValueError('Purchaser field mismatch')
for value in ('待写','待定','待补图','占位','版式演示','草稿','TODO','本轮修改','已验证','检查通过','按你的要求','你提供的材料'):
    if value in text:
        raise ValueError('Editorial residue found')
if pdf.attachments:
    raise ValueError('Source attachments must not enter the publication')
manifest = json.loads((ROOT / 'scripts/illustrations.sha256.json').read_text(encoding='utf8'))
images = {p.name: p for p in (ROOT / 'assets/redacted').glob('*.png')}
if images.keys() != manifest.keys():
    raise ValueError('Unexpected illustration set; review public assets and update manifest')
for name, expected_hash in manifest.items():
    if hashlib.sha256(images[name].read_bytes()).hexdigest() != expected_hash:
        raise ValueError(f'Public illustration changed; review redaction before updating manifest: {name}')
example_build = ROOT / 'tmp/latex-summary'
example_pdf = PdfReader(example_build / 'main.pdf')
example_log = (example_build / 'main.log').read_text(encoding='utf8', errors='replace')
if len(example_pdf.pages) != 1 or example_pdf.attachments:
    raise ValueError('Summary example must be a single page without attachments')
if re.search(r'Overfull \\[hv]box|Missing character:|undefined', example_log):
    raise ValueError('Summary example has unresolved layout or compilation diagnostics')
if (ROOT / 'latex/images/reimbursement-summary.pdf').read_bytes() != (example_build / 'main.pdf').read_bytes():
    raise ValueError('Summary illustration differs from the compiled example')
labels = {}
training_build = ROOT / 'tmp/latex-training-summary'
training_pdf = PdfReader(training_build / 'main.pdf')
training_log = (training_build / 'main.log').read_text(encoding='utf8', errors='replace')
if len(training_pdf.pages) != 1 or training_pdf.attachments:
    raise ValueError('Training summary example must be one page without attachments')
if re.search(r'Overfull \\[hv]box|Missing character:|undefined', training_log):
    raise ValueError('Training summary example has unresolved diagnostics')
if (ROOT / 'latex/images/cross-campus-summary.pdf').read_bytes() != (training_build / 'main.pdf').read_bytes():
    raise ValueError('Training summary illustration differs from the compiled example')
training_text = clean(training_pdf.pages[0].extract_text())
if not all(value in training_text for value in ('40+40+40+40+40', '200元', '5张', '情况说明')):
    raise ValueError('Training summary example fields mismatch')
for label in ('preface','prologue','evidence-chain','invoices','receipts','payment','itinerary','insurance','regular-competition','summary-example','cross-campus-training','training-allowance','appendix-a','epilogue'):
    match = re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{([^}]+)\}', aux)
    if not match or match[1] not in pdf.page_labels:
        raise ValueError(f'Unresolved reference: {label}')
    labels[label] = match[1]
font_notes = re.findall(r'LaTeX Font Warning: Size substitutions with differences\s*\(Font\)\s*up to [\d.]+pt have occurred\.',log)
report = {'engine':'XeLaTeX','pages':len(pdf.pages),'author':pdf.metadata.author,'producer':pdf.metadata.producer,'illustrations':13,'redactedIllustrations':11,'latexExamples':2,'references':labels,'purchaserFieldsMatch':True,'layoutDiagnostics':[],'fontNotes':font_notes}
(build / 'pdf-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))

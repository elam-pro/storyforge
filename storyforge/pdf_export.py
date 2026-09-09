from __future__ import annotations

from pathlib import Path
from textwrap import wrap


# Minimal, dependency-free PDF writer for Latin text. Keeps the app self-contained.
def _pdf_escape(s:str)->str:
    b=s.encode('cp1252','replace').decode('latin1')
    return b.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')

def export_manual_pdf(path:Path, title:str, sections:list[tuple[str,str]]):
    pages=[]
    lines=[title,"Mon manuel d’écriture & storytelling",""]
    for h,body in sections:
        lines += [h]
        for paragraph in (body or "").splitlines():
            if not paragraph.strip(): lines.append(""); continue
            lines += wrap(paragraph, width=88) or [""]
        lines.append("")
    while lines:
        pages.append(lines[:47]); lines=lines[47:]

    objs=[]
    def add(obj:bytes): objs.append(obj); return len(objs)
    font=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    fontb=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    content_ids=[]; page_ids=[]
    for page in pages or [[title]]:
        cmds=["BT","/F1 11 Tf","54 780 Td","15 TL"]
        for i,line in enumerate(page):
            if i==0:
                cmds += ["/F2 18 Tf",f"({_pdf_escape(line)}) Tj","0 -25 Td","/F1 11 Tf"]
            elif line and (line.startswith(("SESSION", "PROJET", "À RETENIR")) or line.endswith(":")):
                cmds += ["/F2 12 Tf",f"({_pdf_escape(line)}) Tj","0 -16 Td","/F1 11 Tf"]
            else:
                cmds += [f"({_pdf_escape(line)}) Tj","0 -15 Td"]
        cmds.append("ET")
        stream="\n".join(cmds).encode('latin1','replace')
        content_ids.append(add(f"<< /Length {len(stream)} >>\nstream\n".encode()+stream+b"\nendstream"))
        page_ids.append(None)
    pages_id=len(objs)+1
    # reserve pages object
    objs.append(b"")
    for idx,cid in enumerate(content_ids):
        pid=add(f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font} 0 R /F2 {fontb} 0 R >> >> /Contents {cid} 0 R >>".encode())
        page_ids[idx]=pid
    kids=" ".join(f"{p} 0 R" for p in page_ids)
    objs[pages_id-1]=f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    catalog=add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
    out=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offsets=[0]
    for i,obj in enumerate(objs,1):
        offsets.append(len(out)); out += f"{i} 0 obj\n".encode()+obj+b"\nendobj\n"
    xref=len(out); out += f"xref\n0 {len(objs)+1}\n".encode()+b"0000000000 65535 f \n"
    for off in offsets[1:]: out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    path.write_bytes(out)

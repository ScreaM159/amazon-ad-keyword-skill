#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WPS DISPIMG 安全写 sheet：只改目标 sheet 的 XML / 其余字节原样，不用 openpyxl 保存（会毁图片）。
用法:
  新增sheet: py write_sheet_safe.py --xlsx 词库.xlsx --sheet 新品期v2 --csv data.csv --mode new
  替换sheet: py write_sheet_safe.py --xlsx 词库.xlsx --sheet 新品期v2 --csv data.csv --mode replace
  csv 第一行为表头，UTF-8。replace 仅建议用于纯数据sheet（无图片/复杂样式）。
"""
import argparse, csv, os, re, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8')

def esc(x):
    return str(x).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def col_letter(i):  # 0-based
    s = ''
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s

def sheet_xml(rows):
    ncols = max(len(r) for r in rows) if rows else 1
    last = f'{col_letter(ncols-1)}{len(rows)}'
    parts = []
    for ri, row in enumerate(rows, 1):
        cells = ''.join(
            f'<c r="{col_letter(ci)}{ri}" t="inlineStr"><is><t xml:space="preserve">{esc(v)}</t></is></c>'
            for ci, v in enumerate(row) if str(v) != '')
        parts.append(f'<row r="{ri}">{cells}</row>')
    NS = ('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
          'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
          'xmlns:etc="http://www.wps.cn/officeDocument/2017/etCustomData">')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + NS +
            f'<sheetPr/><dimension ref="A1:{last}"/><sheetViews><sheetView workbookViewId="0">'
            f'<selection activeCell="A1" sqref="A1"/></sheetView></sheetViews>'
            f'<sheetFormatPr defaultColWidth="16" defaultRowHeight="13.5"/>'
            f'<sheetData>{"".join(parts)}</sheetData>'
            '<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/></worksheet>')

def load_csv(path):
    with open(path, encoding='utf-8-sig') as f:
        return [row for row in csv.reader(f)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', required=True)
    ap.add_argument('--sheet', required=True)
    ap.add_argument('--csv', required=True)
    ap.add_argument('--mode', default='new', choices=['new', 'replace'])
    args = ap.parse_args()

    d = os.path.dirname(os.path.abspath(args.xlsx))
    base = os.path.basename(args.xlsx)
    if os.path.exists(os.path.join(d, '~$' + base)):
        print('LOCKED: 检测到 ~$ 锁文件，请先关闭 WPS/Excel 中的该文件'); sys.exit(2)

    rows = load_csv(args.csv)
    zin = zipfile.ZipFile(args.xlsx, 'r')
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}
    zin.close()

    wbo = data['xl/workbook.xml'].decode('utf-8')
    rels = data['xl/_rels/workbook.xml.rels'].decode('utf-8')
    sheets = re.findall(r'<sheet name="([^"]+)" sheetId="(\d+)" r:id="(rId\d+)"/>', wbo)

    target = None
    for nm, sid, rid in sheets:
        if nm == args.sheet:
            m = re.search(r'Id="%s"[^>]*Target="([^"]+)"' % re.escape(rid), rels)
            if m:
                target = 'xl/' + m.group(1).replace('worksheets/', 'worksheets/')
    xml_new = sheet_xml(rows)

    if args.mode == 'new':
        if target:
            print('EXISTS: sheet 已存在，用 --mode replace 或改名'); sys.exit(2)
    else:
        if not target:
            print('NOTFOUND: 要替换的 sheet 不存在'); sys.exit(2)

    if args.mode == 'replace':
        old = data[target].decode('utf-8')
        if '<sheetData/>' in old:
            old = old.replace('<sheetData/>', re.search(r'<sheetData>.*</sheetData>', xml_new, re.S).group(0), 1)
        else:
            old = re.sub(r'<sheetData>.*?</sheetData>', lambda _: re.search(r'<sheetData>.*</sheetData>', xml_new, re.S).group(0), old, flags=re.S)
        old = re.sub(r'<dimension ref="[^"]*"/>', re.search(r'<dimension ref="[^"]*"/>', xml_new).group(0), old, count=1)
        data[target] = old.encode('utf-8')
    else:
        # 新增：分配 rId / sheetId / sheetN.xml
        max_rid = max([int(x[2][3:]) for x in sheets] + [0])
        max_sid = max([int(x[1]) for x in sheets] + [0])
        used = [int(m.group(1)) for n in names for m in [re.match(r'xl/worksheets/sheet(\d+)\.xml$', n)] if m]
        new_n = max(used + [0]) + 1
        new_path = f'xl/worksheets/sheet{new_n}.xml'
        rid = f'rId{max_rid + 1}'
        sid = max_sid + 1
        wbo = wbo.replace('</sheets>', f'<sheet name="{esc(args.sheet)}" sheetId="{sid}" r:id="{rid}"/></sheets>')
        rels = rels.replace('</Relationships>',
                            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{new_n}.xml"/></Relationships>')
        ct = data['[Content_Types].xml'].decode('utf-8')
        ct = ct.replace('</Types>',
                        f'<Override PartName="/{new_path}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        data['[Content_Types].xml'] = ct.encode('utf-8')
        data['xl/workbook.xml'] = wbo.encode('utf-8')
        data['xl/_rels/workbook.xml.rels'] = rels.encode('utf-8')
        data[new_path] = xml_new.encode('utf-8')
        names.append(new_path)

    tmp = args.xlsx + '.tmp'
    try:
        zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        for n in names:
            zo.writestr(n, data[n])
        zo.close()
        os.replace(tmp, args.xlsx)
    except PermissionError:
        if os.path.exists(tmp):
            os.remove(tmp)
        print('PERMISSION_DENIED: 文件被占用，关闭 WPS 后重试'); sys.exit(2)

    print('OK:', args.sheet, '| 行数', len(rows))
    z = zipfile.ZipFile(args.xlsx)
    print('cellimages 保留:', 'xl/cellimages.xml' in z.namelist(),
          '| media:', sum(1 for n in z.namelist() if n.startswith('xl/media/')))

if __name__ == '__main__':
    main()

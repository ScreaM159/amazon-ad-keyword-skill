#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读词库并校验：字段/分层/相关性统计、缺失ABA、重复、相近写法。只读不改。
用法: py read_wordlib.py --xlsx 词库.xlsx --sheet 词库
"""
import argparse, sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl
from collections import Counter

def norm(x): return str(x).strip() if x is not None else ''

ap = argparse.ArgumentParser()
ap.add_argument('--xlsx', required=True)
ap.add_argument('--sheet', default='词库')
a = ap.parse_args()

wb = openpyxl.load_workbook(a.xlsx, read_only=True, data_only=True)
ws = wb[a.sheet]
rows = list(ws.iter_rows(values_only=True))
wb.close()
hdr = rows[0]
data = [r for r in rows[1:] if r and r[1]]

def idx(names, default):
    for i, h in enumerate(hdr):
        if norm(h) in names: return i
    return default
ikw = idx(['关键词'], 1); ilex = idx(['分层'], 7); irel = idx(['相关性'], 8); iaba = idx(['ABA周排名', 'ABA排名'], 6)

print('表头:', [norm(x) for x in hdr])
print('词数:', len(data))
print('分层:', dict(Counter(norm(r[ilex]) for r in data)))
print('相关性:', dict(Counter(norm(r[irel]) for r in data)))
miss = [norm(r[ikw]) for r in data if not isinstance(r[iaba], (int, float))]
print('缺失ABA:', len(miss), miss[:10])
seen = Counter(norm(r[ikw]).lower() for r in data)
print('重复词:', [k for k, v in seen.items() if v > 1] or '无')
groups = {}
for r in data:
    k = norm(r[ikw]).lower().replace(' ', '')
    groups.setdefault(k, []).append((norm(r[ikw]), r[iaba]))
near = {k: v for k, v in groups.items() if len(v) > 1 and len({str(x[1]) for x in v}) > 1}
print('相近写法ABA不同(勿混用):', near or '无')

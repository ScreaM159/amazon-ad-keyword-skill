#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""关键词分类：先"资格判断"，再给"活动建议"。按列名定位，不硬编码列。
用法:
  py classify_keywords.py --xlsx 词库.xlsx --sheet 词库 --material "rubber" \
     --threshold 350000 --big-threshold 110000 --own-brand "<your-brand>" --competitors "<comp1,comp2>"
说明:
  - threshold / big-threshold 未给时，不做精准判定，标"待确认"。
  - 一个词一条记录；活动建议可多行（1:N），本脚本给"主建议"，多阶段安排另行生成。
"""
import argparse, sys, re
sys.stdout.reconfigure(encoding='utf-8')
try:
    import openpyxl
except ImportError:
    print('缺少 openpyxl'); sys.exit(1)

MATERIAL_ORDER = ['stainless steel', 'powder coated', 'cast iron', 'rubber', 'urethane', 'vinyl', 'steel', 'iron', 'metal']

def norm(x): return str(x).strip() if x is not None else ''

def find_col(hdr, names):
    for i, h in enumerate(hdr):
        if norm(h) in names: return i
    return None

def material_hit(kw):
    kl = kw.lower()
    for t in sorted(MATERIAL_ORDER, key=len, reverse=True):
        if t in kl: return t
    return None

def classify(kw, layer, rel, aba, th, big_t, pm, own, comp):
    kl = kw.lower()
    # 1 自有品牌
    if any(b and b in kl for b in own):
        return ('品牌防御', '品牌防御', '自有品牌，阈值例外')
    # 2 竞品
    cb = next((b for b in comp if b and b in kl), None)
    if cb:
        is_pure = len(kl.replace(cb, '').strip()) <= 3
        if is_pure:
            return ('竞品(纯品牌)', '不投/转ASIN', '纯品牌意图杂，不硬投')
        return ('竞品(品牌+品类)', '精准匹配', '品牌+品类精准/或词组')
    # 3 材质硬性不符（最长优先，避免 cast iron 的 iron 误判）
    mh = material_hit(kw)
    if mh and mh not in pm:
        return ('否定(材质硬性不符)', '否定', '材质不符(%s)' % mh)
    # 4 否定候选/弱相关
    if layer == '否定候选词' or rel in ('弱相关', '不相关'):
        return ('否定', '否定', '否定候选/弱相关')
    # 5 资格：ABA 缺失
    if not isinstance(aba, (int, float)):
        return ('待补ABA', '待定', 'ABA缺失，不判精准')
    if th is None:
        return ('待确认(未给阈值)', '待定', '阈值未给')
    # 6 强相关才可精准；中相关不精准
    if rel == '强相关':
        if big_t is not None and aba <= big_t:
            return ('大词可用', '大词活动', '大词(ABA≤%s)' % big_t)
        if aba <= th:
            return ('可精准', '精准活动', 'ABA≤阈值(%s)' % aba)
        return ('超阈值', '词组/广泛', 'ABA>阈值(%s)' % aba)
    if rel == '中相关':
        return ('不可精准(中相关)', '词组/广泛/待验证', '中相关，需验证')
    return ('待定', '待定', '未匹配规则')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', required=True)
    ap.add_argument('--sheet', default='词库')
    ap.add_argument('--material', default='')
    ap.add_argument('--threshold', type=int, default=None)
    ap.add_argument('--big-threshold', type=int, default=None)
    ap.add_argument('--own-brand', default='')
    ap.add_argument('--competitors', default='')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    pm = set(x.strip().lower() for x in a.material.split(',') if x.strip())
    own = [x.strip().lower() for x in a.own_brand.split(',') if x.strip()]
    comp = [x.strip().lower() for x in a.competitors.split(',') if x.strip()]

    wb = openpyxl.load_workbook(a.xlsx, read_only=True, data_only=True)
    ws = wb[a.sheet]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    hdr = rows[0]
    ikw = find_col(hdr, {'关键词'})
    itr = find_col(hdr, {'关键词翻译', '翻译'})
    ilayer = find_col(hdr, {'分层'})
    irel = find_col(hdr, {'相关性'})
    iaba = find_col(hdr, {'ABA周排名', 'ABA排名', 'ABA周'})
    if None in (ikw, ilayer, irel, iaba):
        print('ERROR: 找不到必要列（关键词/分层/相关性/ABA周排名），请检查表头'); sys.exit(2)

    out, stat = [], {}
    for r in rows[1:]:
        if not r or not r[ikw]:
            continue
        kw = norm(r[ikw]); tr = norm(r[itr]) if itr is not None and itr < len(r) else ''
        layer = norm(r[ilayer]); rel = norm(r[irel]); aba = r[iaba]
        qual, match, note = classify(kw, layer, rel, aba, a.threshold, a.big_threshold, pm, own, comp)
        out.append([kw, tr, layer, rel, aba, qual, match, note])
        stat[qual] = stat.get(qual, 0) + 1

    if a.out:
        import csv
        with open(a.out, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f); w.writerow(['关键词', '翻译', '分层', '相关性', 'ABA', '资格', '建议匹配', '备注']); w.writerows(out)
        print('已写出:', a.out)
    else:
        print('关键词 | 资格 | 建议匹配 | 备注')
        for row in out[:15]:
            print(' | '.join(str(x) for x in [row[0], row[5], row[6], row[7]]))
        print('... 共', len(out), '词（--out 输出完整 CSV）')
    print('\n[资格分布]', stat)
    if a.threshold is None:
        print('[提示] 未给 --threshold：精准判定标"待确认"，不做结论')

if __name__ == '__main__':
    main()

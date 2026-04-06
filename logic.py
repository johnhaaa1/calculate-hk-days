#!/usr/bin/env python3
"""
✅ 100%沿用你的正确计算逻辑
✅ 自动解析移民局PDF（标题+表格都支持）
✅ 直接输出CSV明细文件
✅ 可发给同学通用使用
"""
from datetime import datetime
import pdfplumber
import re
import csv

# ===================== 【你的原版日期函数 - 完全没改】 =====================
def str2dt(d):
    return datetime.strptime(d, '%Y-%m-%d')

# ===================== 【PDF解析 - 生成标准records】 =====================
def parse_pdf(pdf_path):
    records = []
    idx = 1
    date_re = re.compile(r'\d{4}-\d{2}-\d{2}')
    with pdfplumber.open(pdf_path) as f:
        for page in f.pages:
            txt = page.extract_text()
            if not txt: continue
            for line in txt.splitlines():
                line = line.strip()
                if '出境' not in line and '入境' not in line: continue
                dt = date_re.search(line)
                if not dt: continue
                t = '出境' if '出境' in line else '入境'
                port = '未知'
                if '罗湖' in line: port='罗湖口岸'
                elif '莲塘' in line: port='莲塘口岸'
                elif '福田' in line: port='福田口岸'
                elif '深圳湾' in line: port='深圳湾口岸'
                records.append((idx, t, dt.group(), port))
                idx +=1
    return records

# ===================== 【你的原版核心计算 - 一丝不动】 =====================
def calc(records):
    valid = records[1:-1]
    exts = valid[1::2]
    ents = valid[0::2]
    pairs = list(zip(exts, ents))[::-1]
    trips = []
    for s,e in pairs:
        s_idx,_,s_dt,_ = s
        e_idx,_,e_dt,_ = e
        s_d = str2dt(s_dt)
        e_d = str2dt(e_dt)
        days = (e_d - s_d).days +1
        trips.append({'s':s_dt,'e':e_dt,'sd':s_d,'ed':e_d,'days':days})
    # 去重计算
    res = []
    total =0
    for i in range(len(trips)):
        curr = trips[i]
        dup = False
        cut =0
        if i < len(trips)-1 and curr['ed'] == trips[i+1]['sd']:
            dup=True; cut=1
        vd = curr['days']-cut
        total +=vd
        res.append([i+1, curr['s'],curr['e'],curr['days'],'是'if dup else '否',cut,vd,total])
    return res, total

# ===================== 【导出CSV】 =====================
def save_csv(data, path='hk_stay_result.csv'):
    head = ['序号','出境日期','入境日期','单次天数','是否重复','扣减天数','有效天数','累计天数']
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(data)
    print(f'✅ CSV已导出：{path}')

# ===================== 主程序 =====================
if __name__ == "__main__":
    pdf = '1775467490788.pdf'
    rec = parse_pdf(pdf)
    if not rec:
        print('❌ 读取失败')
        exit()
    detail, total = calc(rec)
    # 打印结果
    print('==== 港澳停留天数（你的正确逻辑）====')
    for row in detail:
        print(f"{row[0]:2d} | {row[1]} ~ {row[2]} | 有效{row[6]}d | 累计{row[7]}d")
    print(f'\n🎯 总有效天数：{total} 天')
    print(f'📌 落户180天差额：{max(180-total,0)} 天')
    # 保存CSV
    save_csv(detail)
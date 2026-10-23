#!/usr/bin/env python3
"""将 user_order（用户订单表）填入入湖申请表。

默认值沿用项目历史申请：One蛇口项目组 / 刘琨(产品) / 周佳佳(技术) / cmp_member 库 100.102.1.47:3308。
用法: python3 fill_user_order.py [输出路径]
依赖: openpyxl (pip install openpyxl)
"""
import os
import sys
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side

# ── 路径 ──
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '数据入湖申请表模版.xlsx')
desktop = os.path.expanduser('~/Desktop')
today = datetime.now().strftime('%Y.%m.%d')
today_compact = datetime.now().strftime('%Y%m%d')

# ── 统一样式 ──
FONT_DATA = Font(name='Microsoft YaHei', size=11, bold=False, color='FF333333')
ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
ALIGN_LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)
THIN_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin'),
)


def style_cell(cell, font=FONT_DATA, alignment=ALIGN_LEFT):
    """统一设置单元格样式。"""
    cell.font = font
    cell.alignment = alignment
    cell.border = THIN_BORDER


wb = load_workbook(TEMPLATE)
ws = wb['数据入湖申请表单']

# ── 一、基础申请信息 ──
for ref, val in {'B4': 'One蛇口', 'D4': '刘琨', 'F4': '周佳佳', 'B5': today}.items():
    ws[ref].value = val
    style_cell(ws[ref])

# ── 三、来源数据库信息 ──
for ref, val in {
    'B9': 'MySQL', 'D9': '生产',
    'B10': '100.102.1.47', 'D10': '3308',
    'B11': 'mydb', 'D11': 'mydb',
    'B12': 'cmpmall',
    'B13': '周佳佳',
}.items():
    ws[ref].value = val
    style_cell(ws[ref])

# ── 四、同步表基本信息（Row 18，单表） ──
DDL = """CREATE TABLE `mydb`.`user_order` (
  `id` varchar(64) NOT NULL COMMENT '主键',
  `user_id` varchar(64) NOT NULL COMMENT '用户ID',
  `order_no` varchar(64) COMMENT '订单号',
  `amount` decimal(10,2) COMMENT '订单金额',
  `status` int DEFAULT '0' COMMENT '订单状态',
  `create_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_date` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `delete_flag` tinyint(1) DEFAULT '0' COMMENT '删除标记',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB COMMENT='用户订单表'"""

table1 = {
    'B': 'user_order',
    'C': '用户订单表',
    'D': '小表',
    'E': '小表',
    'F': DDL,
    'G': 'id',
    'H': '否（逻辑删除 delete_flag）',
    'I': '增量',
    'J': '每日一次',
    'K': 'update_date',
    'L': '需要',
    'M': '—',
    'N': '定时更新(update_date)',
}

cell_a = ws.cell(row=18, column=1)
cell_a.value = 1
style_cell(cell_a, FONT_DATA, ALIGN_CENTER)
for col_letter, val in table1.items():
    cell = ws.cell(row=18, column=ord(col_letter) - ord('A') + 1)
    cell.value = val
    style_cell(cell)
ws.row_dimensions[18].height = 29.1

# ── 五、其他信息 ──
for ref, val in [
    ('B30', '尽快'),
    ('B31', '新增用户订单表入湖，支撑订单分析'),
]:
    ws[ref].value = val
    style_cell(ws[ref])

# ── 六、授权需求和抽数频率及时间 ──
auth = {'A': 'One蛇口', 'B': 'cmsk_super_app', 'C': today, 'D': '每日一次',
        'E': '无特别需求，入湖同学根据资源情况自行安排'}
for col_letter, val in auth.items():
    cell = ws.cell(row=36, column=ord(col_letter) - ord('A') + 1)
    cell.value = val
    style_cell(cell)

# ── 表结构说明模板 ──
ws3 = wb['表结构说明模板']
for mr in list(ws3.merged_cells.ranges):
    if mr.min_row >= 2:
        ws3.unmerge_cells(str(mr))
for r in range(2, 201):
    for c in range(1, 5):
        ws3.cell(row=r, column=c).value = None

fields = [
    ('id', 'varchar(64)', '主键'),
    ('user_id', 'varchar(64)', '用户ID'),
    ('order_no', 'varchar(64)', '订单号'),
    ('amount', 'decimal(10,2)', '订单金额'),
    ('status', 'int', '订单状态（默认0）'),
    ('create_date', 'datetime', '创建时间（DEFAULT CURRENT_TIMESTAMP）'),
    ('update_date', 'datetime', '更新时间（ON UPDATE CURRENT_TIMESTAMP，增量同步依据）'),
    ('delete_flag', 'tinyint(1)', '删除标记（0-未删除 1-已删除）'),
]

n = len(fields)
ws3.merge_cells(start_row=2, start_column=1, end_row=2 + n - 1, end_column=1)
style_cell(ws3.cell(row=2, column=1), FONT_DATA, ALIGN_LEFT)
ws3.cell(row=2, column=1).value = 'user_order\n（用户订单表）'
for i, (fn, ft, fd) in enumerate(fields):
    r = 2 + i
    for c in (2, 3, 4):
        style_cell(ws3.cell(row=r, column=c))
    ws3.cell(row=r, column=2).value = fn
    ws3.cell(row=r, column=3).value = ft
    ws3.cell(row=r, column=4).value = fd

# ── 保存 ──
output_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(desktop, f'数据入湖申请表_One蛇口_{today_compact}.xlsx')
wb.save(output_path)
print(f'✅ 已生成: {output_path}')
print(f'字段数: {n}')

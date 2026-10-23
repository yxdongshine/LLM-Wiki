# 操作日志

## [2026-09-25] query | 初始化知识库并生成学习指南
- **变更**: 新增 [[llm-wiki架构学习与上手指南]]; 初始化 [[index.md]] 和 [[log.md]]
- **冲突**: 无

## [2026-09-25] query | 入湖技能演示 — user_order 表
- **变更**: 新增 `skills/入湖/fill_user_order.py`（参照 fill_activity_signin_result.py 模式）
- **输出**: ✅ 已生成 `~/Desktop/数据入湖申请表_One蛇口_20261023.xlsx`（8 字段，三 Sheet）
- **环境**: Python 3.14.3 + openpyxl 3.1.5（路径 C:\D\tools\Python\path\python.exe）
- **冲突**: 无

## [2026-09-25] sync | 安装 skill-creator 工具
- **变更**: 全局安装 skill-creator@2.6.0 (npm)；运行 setup 链接 self-skill + 注入 AGENTS.md guidance
- **环境**: Node.js npm 全局安装，路径 C:\Users\Administrator\AppData\Roaming\npm\node_modules\skill-creator
- **冲突**: 无

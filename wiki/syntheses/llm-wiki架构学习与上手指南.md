---
title: "LLM-Wiki 架构学习与上手指南"
type: synthesis
tags: [架构学习, 上手指南, Agent技能, Obsidian知识库, 框架改造]
sources: ["AGENTS.md", "skills/ingest/SKILL.md", "skills/query/SKILL.md", "skills/lint/SKILL.md", "skills/取数/SKILL.md", "skills/sql-etl-review/SKILL.md", "skills/sql-formatter/SKILL.md", "skills/需求文档/SKILL.md", "skills/数据补数/SKILL.md", "skills/入湖/SKILL.md", "skills/数据补数/backfill.py", "skills/入湖/generate_ingest_excel.py"]
last_updated: 2026-09-25
---

# LLM-Wiki 架构学习与上手指南

> [!abstract] 核心观点
> 本项目是一个"以 AI Agent 技能为操作层、Obsidian 双链知识库为存储层、AGENTS.md 为契约层"的个人知识工程框架。它的精髓不在于某个具体脚本，而在于一套**用 Markdown 定义 Agent 工作流**的范式，以及配套的**证据分级、确认闸门、双向链接、追加日志**等工程纪律。改造为自己项目时，保留三层架构与技能范式，替换领域内容即可。

---

## 第一部分：项目全貌——它到底是什么

### 1.1 一句话定位

这不是一个传统意义上的"代码项目"（没有 main 函数、没有编译产物），而是一个**给 AI Agent 用的"操作系统级配置仓库"**。它告诉各种 AI 编程助手（Claude Code / Codex / DSH / WorkBuddy）：在这个知识库里，你应该怎么摄取资料、怎么检索、怎么写 SQL、怎么补数据、遇到冲突怎么办。

### 1.2 三层架构

```
┌─────────────────────────────────────────────────────────┐
│  契约层：AGENTS.md（最高规范，定义语言、目录权限、证据规则）    │
├─────────────────────────────────────────────────────────┤
│  操作层：skills/（每个 SKILL.md = 一个 Agent 可调用的技能）   │
│          通过软链接暴露给 .claude/ .codex/ .dsh/ .workbuddy │
├─────────────────────────────────────────────────────────┤
│  存储层：raw/（只读源）→ wiki/（编译输出）→ assets/（媒体）  │
│          wiki/ 内部按 sources/entities/concepts/syntheses │
│          四分类组织，Obsidian 双链互联                      │
└─────────────────────────────────────────────────────────┘
```

| 目录 | 角色 | 权限 |
|---|---|---|
| `raw/` | 原始素材（网页剪藏、文档、SQL 脚本） | **绝对只读**，不可修改 |
| `wiki/` | Agent 编译输出的知识页 | Agent 的专属工作区，可读写 |
| `assets/` | 图片、PDF 等媒体 | 用 `![[文件名.png]]` 引用 |
| `skills/` | Agent 技能定义（SKILL.md + 辅助脚本） | 技能的唯一真源 |

### 1.3 技能注册表与跨平台分发

本项目最巧妙的设计之一是**技能的跨平台分发机制**：

```
skills/                          # 唯一真源（在这里写一次）
├── .dsh/skills -> ../skills      # DSH 平台通过软链接发现
├── .codex/skills -> ../skills    # Codex 平台
├── .workbuddy/skills -> ../skills
└── .claude/skills -> ../skills   # Claude Code 平台
```

> **学习点**：写一次技能，所有 AI 平台都能用。新增平台只需建一个软链接，不用同步文件。这是"配置即代码"在 AI Agent 领域的实践。

---

## 第二部分：九大关键技能点提炼

### 技能点 1：技能定义范式（SKILL.md 结构）

这是整个项目最核心的可复用模式。每个技能都是一个自包含的 Markdown 文件：

**文件位置**：[`skills/ingest/SKILL.md`](skills/ingest/SKILL.md:1)、[`skills/query/SKILL.md`](skills/query/SKILL.md:1) 等

**标准结构**：
```yaml
---
name: 技能名                 # 唯一标识
description: 触发描述        # 告诉 Agent 什么时候该用这个技能
user-invocable: true         # 是否可被用户直接调用
tags: [标签]                 # 可选分类
---

# 技能标题

## 目标        ← 这个技能要解决什么问题
## 触发方式    ← 自然语言触发词 + 斜杠命令
## 工作流      ← 分步骤的 SOP（标准操作流程）
## 禁止事项    ← 红线规则
## 完成标准    ← 验收条件
```

> **学习点**：`description` 字段是技能被"发现"的关键——它既是触发条件说明，也是语义匹配的依据。写得越精准，Agent 误触发越少。对比 [`skills/数据补数/SKILL.md`](skills/数据补数/SKILL.md:3) 的 description（明确列出触发场景和脚本路径）vs 简单的 "数据补数工具"，差距很大。

### 技能点 2：确认闸门（Confirmation Gate）模式

多个技能中都内置了"强制确认闸门"——在执行高影响操作前，必须停下来等用户明确确认。这是**生产安全**的关键设计。

**三个典型闸门技能**：

| 技能 | 闸门数量 | 闸门内容 | 文件位置 |
|---|---|---|---|
| [取数](skills/取数/SKILL.md:70) | 3 个 | 取数方案→输出结构→交付形式 | `skills/取数/SKILL.md:70` |
| [数据补数](skills/数据补数/SKILL.md:103) | 1 个 | 补数计划确认 | `skills/数据补数/SKILL.md:103` |
| [入湖](skills/入湖/SKILL.md:51) | 多个 | 逐项确认元信息 | `skills/入湖/SKILL.md:51` |

**闸门的硬性规则**（以取数为例，[`skills/取数/SKILL.md:101`](skills/取数/SKILL.md:101)）：

```
✅ 视为已确认：明确说"确认""可以""没问题""继续""就这么办"
❌ 视为未确认：模糊的"好""OK""嗯"、只提供参数未说确认
```

> **学习点**：这种设计防止了 Agent 在"主动执行模式"下失控。即使你让它"放手干"，碰到生产环境操作（补数、写 SQL）时，它仍然会先展示计划、等你说"确认"才执行。这是"信任但不放任"的工程哲学。

### 技能点 3：证据分级体系（L1/L2/L3）

这是项目最独特的反幻觉机制，定义在 [`AGENTS.md`](AGENTS.md:1) 的"事实依据规则"中：

| 等级 | 定义 | 示例 |
|---|---|---|
| **L1 权威证据** | DDL 字段注释、脚本原文、SQL 的 FROM/JOIN 子句、主人口述 | `one_user_id（cmp_user DDL 注释：用户中心用户id）` |
| **L2 可追溯推断** | 由 L1 的 Join 条件、别名映射反推的关系 | 由 JOIN 条件推导两表关联 |
| **L3 无依据猜测** | "这类表通常有 X 字段"的模式补全 | ❌ 禁止使用 |

**执行要求**（[`AGENTS.md`](AGENTS.md:1)）：
1. 每个实体（表名/字段名）必须能指到 L1 证据，指不到就不写
2. 证据不足时输出 `<?待确认>` 占位符，**留白优于填充**
3. 所有实体后附来源坐标：`表名（SQL文件:行号，JOIN类型）`

> **学习点**：这套体系源于两次真实事故（2026-08-31 编造字段、2026-09-03 编造血缘节点）。它把"禁止幻觉"从口号变成了可执行规则。任何 AI 知识库项目都可以直接复用这套证据分级。

### 技能点 4：双向链接与反孤岛

每个 wiki 页面**必须**包含 `## 关联连接` 区域，使用 Obsidian 双链 `[[页面名]]`。这确保知识库是一张网，而不是一堆孤岛。

**页面间的链接类型**：
```
Source 页 → Entity/Concept 页    （资料提炼出实体和概念）
Concept 页 ↔ Concept 页          （上下位概念、对比概念）
Synthesis 页 → 所有引用页         （综合分析引用多页结论）
```

配套的 [`lint`](skills/lint/SKILL.md:101) 技能会扫描孤岛页面（没有任何入链的页面）和死链（链接指向不存在的页面），保证知识库的健康度。

> **学习点**：知识库的价值在于连接，不在于堆积。双链 + 定期 lint = 可维护的知识网络。

### 技能点 5：追加式操作日志

[`wiki/log.md`](wiki/log.md:1) 是 append-only 的操作记录，每次操作后必须追加：

```markdown
## [2026-09-25] ingest | 引入项目核心概念
- **变更**: 新增 [[某概念]]; 更新 [[index.md]]
- **冲突**: 无
```

操作类型固定为 `ingest` / `query` / `lint` / `sync`，格式固定为 `## [日期] 动作 | 简述`。

> **学习点**：日志不是给人看的"流水账"，而是给 Agent 看的"操作记忆"。当 Agent 需要回答"之前摄取过什么""上次查询了什么"时，日志就是事实来源。append-only 保证历史不可篡改。

### 技能点 6：Ingest 摄取流水线

[`skills/ingest/SKILL.md`](skills/ingest/SKILL.md:69) 定义了一条完整的资料编译流水线，这是知识库的"输入"机制：

```
raw/ 原始资料
  │
  ├─ 1. 预检与去重（检查是否已摄取）
  ├─ 2. 读取资料（按格式：md/txt/pdf/docx/源码目录）
  ├─ 3. 提炼知识（核心主旨 + 关键要点 + Entities + Concepts）
  ├─ 4. 创建 Source 页（中文命名，带 Frontmatter）
  ├─ 5. 增量维护 Entity/Concept（不覆盖，只增量合并）
  ├─ 6. 处理知识冲突（暂停→报告→等用户选择）
  ├─ 7. 同步全局索引（更新 index.md）
  ├─ 8. 记录操作日志（追加 log.md）
  └─ 9. 归档源文件（移到 raw/99-archive/）
```

**关键设计**：每个源单元是独立事务——页面、索引、日志全部成功后才归档。一个文件失败不阻止其他文件完成。

> **学习点**：这个流水线把"碎片化信息→结构化知识"的过程工程化了。它的去重、冲突处理、增量合并机制，是手工整理笔记时最容易出错的地方。

### 技能点 7：Query 检索与降级策略

[`skills/query/SKILL.md`](skills/query/SKILL.md:40) 定义了本地知识检索的分层策略：

```
① 解析问题（识别主题、同义词、中英文缩写）
② 必须先读全局索引（index.md 是检索第一入口）
③ 索引为空时降级（扫描目录文件名和 Frontmatter）
④ 分层扩展检索（精确匹配→标题标签→正文关键词→沿双链扩展）
⑤ 深读候选页面（完整读取，不只看摘要）
⑥ 综合回答（区分本地知识/推断/冲突/缺口）
```

**降级声明**（[`skills/query/SKILL.md:141`](skills/query/SKILL.md:141)）：
> 本地知识库中未找到，以下为通用知识回答。

> **学习点**：这个设计解决了 AI 回答时"混淆本地知识和通用知识"的问题。它强制 Agent 先查本地，查不到才用通用知识，并明确声明来源类型。回答中用 `[[wikilink]]` 标注本地依据，让用户能追溯。

### 技能点 8：Python 脚本的工程实践

项目中包含两类 Python 脚本，展示了不同的工程模式：

**模式 A：参数化命令行工具**（[`skills/数据补数/backfill.py`](skills/数据补数/backfill.py:1)）
- 用 `argparse` 定义所有参数
- 凭据从**环境变量**读取（`DATA_ASSET_JWT`），不硬编码
- 内置 `--dry-run` 预检模式
- 异常自停机制（token 失效立即 `sys.exit(1)`）
- 完整的成功/失败统计与日志落盘

**模式 B：模板填充生成器**（[`skills/入湖/generate_ingest_excel.py`](skills/入湖/generate_ingest_excel.py:1)）
- 基于 Excel 模版，**清空数据区但保留样式**
- `DEFAULTS` 字典集中管理默认值
- 用 `openpyxl` 操作单元格，样式与数据分离
- `copy()` 复制样式对象避免引用共享

> **学习点**：这两个脚本展示了"技能可携带可执行代码"的设计。SKILL.md 是"说明书"，Python 脚本是"执行器"，两者一起分发。Agent 读完 SKILL.md 知道怎么调用，脚本保证执行的一致性。

### 技能点 9：安全与凭据管理

[`skills/数据补数/SKILL.md`](skills/数据补数/SKILL.md:119) 中的凭据管理是安全实践的范本：

```
✅ 推荐：环境变量注入，不落盘
   DATA_ASSET_JWT='<jwt>' python3 backfill.py ...

✅ 可选：命令行 --jwt/--cookie（注意会留在 shell history）

❌ 禁止：写入 SKILL.md、wiki、docs 或任何提交到仓库的文件
```

配套的 **token 预检机制**（[`skills/数据补数/SKILL.md:131`](skills/数据补数/SKILL.md:131)）：全量执行前先发 1 次单日请求验证 token 是否有效，防止跨天失效后空转。

> **学习点**：AI Agent 操作生产系统时，凭据安全是底线。这个项目的做法是"技能说明规则 + 脚本强制执行"，形成双重保障。

---

## 第三部分：技能体系全景图

项目当前包含 9 个技能，分属三大类：

### 知识库维护类（4 个）

| 技能 | 触发 | 核心职责 |
|---|---|---|
| [`ingest`](skills/ingest/SKILL.md:1) | `/ingest <路径>` | raw/ → wiki/ 编译，自动归档 |
| [`query`](skills/query/SKILL.md:1) | `/query <问题>` | 检索本地 Wiki 并引用回答 |
| [`lint`](skills/lint/SKILL.md:1) | `/lint` | 死链/孤岛/索引健康检查 |
| [`需求文档`](skills/需求文档/SKILL.md:1) | `/需求文档 <内容>` | 任意输入→结构化需求文档 |

### 数仓取数类（3 个）

| 技能 | 触发 | 核心职责 |
|---|---|---|
| [`取数`](skills/取数/SKILL.md:1) | `/取数 <需求>` | 七步 SOP 写有证据的取数 SQL |
| [`sql-etl-review`](skills/sql-etl-review/SKILL.md:1) | "提交 SQL Review" | 按 Team 规范评审 Hive/Spark SQL |
| [`sql-formatter`](skills/sql-formatter/SKILL.md:1) | `/sql-format` | SQL 格式化与风格统一 |

### 数据工程类（2 个）

| 技能 | 触发 | 核心职责 |
|---|---|---|
| [`数据补数`](skills/数据补数/SKILL.md:1) | "补数据""回刷" | 逐日触发调度任务补数 |
| [`入湖`](skills/入湖/SKILL.md:1) | `/入湖` | 生成数据入湖申请 Excel |

> **学习点**：技能按"维护知识库 → 用知识库干活 → 工程化操作"三层递进。前 4 个是通用框架（任何知识库都需要），后 5 个是领域专用（数仓/数据工程）。改造时，保留前 4 个，替换后 5 个。

---

## 第四部分：如何改造为你自己的项目

### 4.1 改造策略总览

```
保留（通用框架）          替换（领域内容）           删除（看需求）
─────────────────       ─────────────────        ─────────────
AGENTS.md 契约结构       数仓相关技能              不用的平台软链接
三层目录架构             具体业务表名/字段         macOS 专属脚本路径
ingest/query/lint        取数/ETL/入湖技能         数据补数（如无调度平台）
技能定义范式             raw/ 中的业务资料
证据分级体系             index.md 中的分类
确认闸门模式
双链 + 模板
```

### 4.2 分步上手指南

#### 第 1 步：理解契约，修改 AGENTS.md

AGENTS.md 是整个项目的"宪法"。你需要修改的部分：

1. **语言设定**：当前是简体中文，如果你的项目用英文，改语言指令
2. **角色定义**：把"LLM Wiki 维护者"改成你的角色定位
3. **目录结构权限**：如果你的项目不需要 `raw/` 只读层，可以调整
4. **事实依据规则**：这套 L1/L2/L3 证据分级**强烈建议保留**，它是反幻觉的核心
5. **技能注册表**：删除你不需要的平台行，保留你用的平台

#### 第 2 步：清理领域专用技能

```bash
# 删除数仓/数据工程类技能（如果你不做数据工程）
# 在 Windows CMD 中：
rmdir /s /q "skills\取数"
rmdir /s /q "skills\sql-etl-review"
rmdir /s /q "skills\sql-formatter"
rmdir /s /q "skills\数据补数"
rmdir /s /q "skills\入湖"
```

保留 `skills/ingest/`、`skills/query/`、`skills/lint/`、`skills/需求文档/` 四个通用技能。

#### 第 3 步：创建你自己的领域技能

参照 [`skills/ingest/SKILL.md`](skills/ingest/SKILL.md:1) 的结构，创建你的第一个技能：

```yaml
---
name: 你的技能名
description: 明确写出触发场景。例如"当用户要求做X时使用此技能。
             支持斜杠命令 /你的命令。核心流程：第一步...第二步..."
user-invocable: true
---

# 技能标题

## 目标
[这个技能解决什么问题]

## 触发方式
- `/你的命令`
- "自然语言触发词1"
- "自然语言触发词2"

## 工作流
### 第一步：[动作]
[详细说明]

### 第二步：[动作]
[详细说明]

## 禁止事项
- [红线规则]

## 完成标准
- [ ] [验收条件1]
- [ ] [验收条件2]
```

> **技能设计要点**：
> 1. `description` 要写得像一个"招聘启事"——告诉 Agent 什么时候该"应聘"
> 2. 工作流用编号步骤，每步有明确的输入输出
> 3. 涉及危险操作时加"确认闸门"
> 4. 如果技能需要执行代码，把脚本放在技能目录下（如 `skills/你的技能/your_script.py`）

#### 第 4 步：初始化你的知识库

```bash
# 确保目录结构存在（Windows CMD）
mkdir "wiki\sources" "wiki\entities" "wiki\concepts" "wiki\syntheses"
```

创建 `wiki/index.md`（参照 AGENTS.md 中的格式）：

```markdown
# Wiki Index

## Sources
（空，ingest 后自动填充）

## Entities
（空）

## Concepts
（空）

## Syntheses
- [[llm-wiki架构学习与上手指南]] — 本框架的架构分析与改造指南
```

创建 `wiki/log.md`：

```markdown
# 操作日志

## [2026-09-25] query | 初始化知识库
- **输出**: 创建 index.md 和 log.md，录入学习指南
```

#### 第 5 步：配置平台软链接

根据你使用的 AI 平台，创建对应的软链接。在 Windows 中（需要管理员权限或开发者模式）：

```cmd
# 如果用 Claude Code
mklink /D ".claude\skills" "..\skills"

# 如果用 Codex
mklink /D ".codex\skills" "..\skills"
```

> **注意**：Windows 的 `mklink` 需要管理员权限。也可以不用软链接，直接在平台配置中指定 skills 路径。

#### 第 6 步：放入原始资料，开始摄取

把你的学习资料、项目文档放入 `raw/` 下（按主题建子目录），然后对 AI Agent 说：

> "摄取 raw/ 下的资料" 或 `/ingest`

Agent 会自动执行 ingest 流水线，把资料编译成 wiki 页面。

### 4.3 改造检查清单

改造完成后，用以下清单自检：

- [ ] AGENTS.md 已更新为你的角色和语言设定
- [ ] 证据分级规则（L1/L2/L3）已保留
- [ ] 不需要的领域技能已删除
- [ ] 至少保留 ingest / query / lint 三个通用技能
- [ ] 已创建至少一个你自己的领域技能
- [ ] `wiki/index.md` 和 `wiki/log.md` 已初始化
- [ ] `raw/` 目录已放入你的第一批资料
- [ ] 平台软链接已配置（如需要）
- [ ] 对 Agent 说 `/lint` 能正常返回健康检查报告

### 4.4 进阶：技能编写最佳实践

从本项目提炼的技能编写经验：

| 实践 | 说明 | 参考示例 |
|---|---|---|
| **description 要长且具体** | 列出所有触发场景和关键词 | [`skills/数据补数/SKILL.md:3`](skills/数据补数/SKILL.md:3) |
| **工作流用编号步骤** | 每步有明确输入→输出 | [`skills/取数/SKILL.md:33`](skills/取数/SKILL.md:33) 七步 SOP |
| **危险操作加闸门** | 展示计划→等确认→才执行 | [`skills/数据补数/SKILL.md:103`](skills/数据补数/SKILL.md:103) |
| **区分确认 vs 模糊** | 明确列出哪些措辞算确认 | [`skills/取数/SKILL.md:101`](skills/取数/SKILL.md:101) |
| **禁止事项写红线** | 哪些事绝对不能做 | [`skills/入湖/SKILL.md:138`](skills/入湖/SKILL.md:138) |
| **完成标准可勾选** | 用 `- [ ]` 列验收条件 | [`skills/数据补数/SKILL.md:183`](skills/数据补数/SKILL.md:183) |
| **脚本随技能分发** | SKILL.md + .py 放同一目录 | `skills/数据补数/backfill.py` |
| **凭据走环境变量** | 不硬编码到任何文件 | [`skills/数据补数/SKILL.md:119`](skills/数据补数/SKILL.md:119) |

---

## 第五部分：学习路径建议

如果你是初次接触这类项目，建议按以下顺序学习：

### 阶段一：理解框架（1-2 天）

1. 通读 [`AGENTS.md`](AGENTS.md:1)——这是总规范，理解三层架构和证据规则
2. 读 [`skills/ingest/SKILL.md`](skills/ingest/SKILL.md:1)——理解知识是怎么"输入"的
3. 读 [`skills/query/SKILL.md`](skills/query/SKILL.md:1)——理解知识是怎么"检索"的
4. 读 [`skills/lint/SKILL.md`](skills/lint/SKILL.md:1)——理解知识库怎么"维护"的

### 阶段二：动手实践（3-5 天）

5. 放入 2-3 份你自己的资料到 `raw/`，执行 `/ingest`
6. 用 `/query` 查询刚摄取的知识，观察双链和引用
7. 执行 `/lint` 检查知识库健康度
8. 尝试修改一个技能的 `description`，观察触发行为变化

### 阶段三：改造定制（1 周）

9. 删除不需要的领域技能
10. 编写你的第一个领域技能（参照第四部分的模板）
11. 更新 AGENTS.md 为你的角色设定
12. 持续摄取资料，建立你的知识网络

### 阶段四：深入进阶

13. 研究 [`skills/取数/SKILL.md`](skills/取数/SKILL.md:1) 的七步 SOP 和三闸门设计
14. 研究 [`skills/sql-etl-review/SKILL.md`](skills/sql-etl-review/SKILL.md:1) 的"三行粒度"强制规则
15. 学习 [`skills/数据补数/backfill.py`](skills/数据补数/backfill.py:1) 的参数化和安全设计
16. 尝试为你的技能编写配套的 Python 脚本

---

## 关联连接

- **框架契约**：[[AGENTS规范]] — 项目的最高规范文件（待建为 Concept 页）
- **核心技能**：[[Ingest技能]]、[[Query技能]]、[[Lint技能]] — 知识库三大通用技能（待建为 Concept 页）
- **关键概念**：[[证据分级体系]] — L1/L2/L3 反幻觉机制（待建为 Concept 页）
- [[确认闸门模式]] — 生产安全的关键设计模式（待建为 Concept 页）
- [[Obsidian双向链接]] — 知识网络的基础设施（待建为 Concept 页）
- [[技能定义范式]] — SKILL.md 的标准结构（待建为 Concept 页）

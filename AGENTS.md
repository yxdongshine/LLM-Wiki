# LLM Wiki 维护规范（Agent 指南）

> 本文件定义 LLM Wiki 知识库的统一维护规则。任何 Agent（如 Codex）或人工贡献者在修改本库前，必须先阅读并遵守本规范。

## 语言设定与核心角色

- **语言指令**：无论输入何种语言，你必须始终使用**简体中文**进行思考、回复和知识库编写。
- **角色定义**：你正在维护一个 LLM Wiki，任务是将碎片化的信息编译成结构化、高度相互链接的 Obsidian 知识库。

## 目录结构与权限边界

| 目录 | 层级 | 职责与权限 |
|---|---|---|
| `raw/` | 不可变层（Immutable） | **绝对只读**。存放原始素材、网页剪藏和自媒体文案；**禁止修改或删除**任何文件，它是事实的唯一真相来源。 |
| `assets/` | 媒体资产层 | 存放图片、PDF 和媒体；引用时使用 Obsidian 标准语法 `![[文件名称.png]]`。 |
| `wiki/` | 编译输出层（You Own This） | 你的专属工作区；在此创建、更新、提炼知识并解决矛盾。 |

## Wiki 核心文件契约

### `wiki/index.md`（总目录）

每次向 wiki 新增知识页后，必须同步更新，将其按分类加入目录：

- 格式：`[[页面名称]] — 一句话描述`
- 命名：Entities / Concepts 使用 TitleCase；Sources / Syntheses 使用 kebab-case

```markdown
# Wiki Index

## Sources
- [[摘要-source-slug]] — 该资料的核心主旨摘要。

## Entities
- [[EntityName]] — 该实体的身份定义或核心功能。

## Concepts
- [[ConceptName]] — 该概念或框架的核心定义。

## Syntheses
- [[synthesis-slug]] — 该页面回答的复杂问题。
```

### `wiki/log.md`（操作日志）

只能追加写入（Append-only）。每次操作后记录：`## [YYYY-MM-DD] <动作> | <操作简述>`，操作类型为 `ingest` / `query` / `lint` / `sync`：

```markdown
## [2026-04-11] ingest | 引入项目 Codex 核心概念
- **变更**: 新增 [[Codex]], [[摘要-codex-docs]]; 更新 [[index.md]]
- **冲突**: 无 (或: 冲突 [[RAG架构]], 已标注)

## [2026-04-11] query | 解析 Karpathy LLM-Wiki 理念
- **输出**: 已保存至 [[分析-karpathy-wiki-philosophy]]

## [2026-04-11] lint | 周度健康检查
- **结果**: 修复 2 处死链，发现 1 个孤儿页面 [[UnlinkedPage]]
```

### 内容分类

- `wiki/concepts/`：概念、框架、方法论（如 `Agent_Skill.md`）
- `wiki/entities/`：人物、公司、工具、产品（如 `Codex.md`）
- `wiki/sources/`：从 `raw/` 提炼出的原始素材摘要

### 强制双向链接

每一个 wiki 页面必须包含 `## 关联连接` 区域，使用 Obsidian 双链 `[[页面名称]]` 链接到其他相关概念；绝不能产生孤岛页面。

### 矛盾处理原则

如果新摄入的知识与旧知识冲突，不要静默覆盖。在页面中新建 `## 知识冲突` 区块，将两种说法都保留并做对比。

### 事实依据规则（强制，最高优先级）

**本知识库的一切生成内容必须有可追溯的事实来源。禁止凭空编造任何表名、字段名、依赖关系、SQL 逻辑、图形节点或任何数据资产细节。**

2026-08-31 事故：回答中编造了 `hd17_one_user_community_customer_tag_ss.user_id`（实际字段为 `one_user_id`）、`COALESCE(user_id, owner_id)`（现网无此逻辑），均因凭"这类表通常有 X 字段"的模式补全而非查证。

2026-09-03 事故：生成 ARIES 血缘图时编造了 `HAEST0101_QJDT_MEETING_SS`（签到会议）、`hoest0154_customer_account_ss`（业主认证）、`hoest0161_customer_account_ss`（招商荟会员）、`HD17_ONE_USER_COMMUNITY_CUSTOMER_TAG_SS`（社区标签）共 4 个虚假节点及 6 条虚假依赖边。均因凭"这类场景通常还有这些表"的模式补全，未逐行查证目标 SQL 的 FROM/JOIN 子句。

#### 适用范围

本规则适用于所有生成内容，包括但不限于：SQL 查询、数据血缘图、ER 图、架构图、数据字典、取数口径、表结构说明、字段映射文档。

#### 证据分级

| 等级 | 定义 | 可用范围 |
|---|---|---|
| 1 | **L1 权威证据** | 表 DDL 的字段注释、现网调度脚本原文、数据字典字段注释、SQL 文件的 FROM/JOIN 子句、主人明确口述的口径 |
| 2 | **L2 可追溯推断** | 由 L1 证据的 join 条件、别名映射、字段注释、CTE 引用链反推得出的关系 |
| 3 | **L3 无依据猜测** | 模式补全（"这类表通常有 X"、"这个场景一般还缺 Y"）、跨表类比、凭印象复用 |

#### 执行要求

1. **生成任何内容前，每个实体（表名/字段名/节点）必须能指到 L1 证据**。指不到 → 不写，改列「待确认」清单请主人确认。
2. **留白优于填充**。证据不足时，输出 `<?待确认>` 占位符或"待确认问题"小节，绝不用"看起来合理"的内容补位。
3. **标注证据坐标**。所有实体后附来源，格式：`表名（SQL 文件:行号，JOIN/FROM 类型）`。如 `hoest0134_aries_profiles_cs（ha17_aries_profiles_cs.sql:117，JOIN）`。
4. **跨表禁止字段串味**。名字相似的表（如 `hoest0154_customer_account_ss` 与 `hoest0161_customer_account_ss`）字段不可互相套用，各自查证。
5. **别名 ≠ 字段**。脚本中 `user_id AS one_user_id` 只说明输出别名，不代表源表有 `one_user_id` 字段。
6. **主人纠正即 L1**。主人明确指出的口径直接升为 L1，记入当日 memory 并覆盖原有推断。
7. **血缘图/架构图专项**：每个节点必须能追溯到 SQL 文件的 FROM/JOIN 子句或 DDL 表定义；每条边必须能追溯到具体的 JOIN 条件。禁止添加"看起来有关联"的节点或边。

## 工作流指令

| 指令 | 行为 |
|---|---|
| `/ingest <路径>` | 读取指定的 `raw/` 文件，将其核心价值提炼并整合到 `wiki/` 目录的相关概念/实体中；必须更新 index 和 log。 |
| `/query <问题>` | 读取 `wiki/index.md` 寻找相关文件，深度阅读后综合回答，并在回答中使用 `[[wikilink]]` 标注引用来源。 |
| `/lint` | 全局扫描 `wiki/` 目录，找出孤岛页面（无双链）、死链（链接不存在的页面）以及逻辑冲突，并向我报告。 |

## Skills 注册表

> 所有技能统一存放在 `skills/` 目录，通过软链接暴露给各平台：
>
> | 平台 | 扫描路径 | 发现机制 | 状态 |
> |---|---|---|---|
> | DSH | `.dsh/skills -> ../skills` | 项目级软链接 | ✅ 已建立（2026-09-23） |
> | Codex | `.codex/skills -> ../skills` | 项目级软链接 | ✅ |
> | Claude Code | `.claude/skills -> ../skills` | 项目级软链接 | ✅ |
> | WorkBuddy | `.workbuddy/skills -> ../skills` | 项目级软链接 | ✅ |
>
> ⚠️ **新增技能只需在 `skills/` 下创建子目录，无需同步到各平台**；但新增**平台**时必须确认该平台的扫描路径，否则技能不会被发现。

### Wiki 知识库维护

| 技能 | 触发方式 | 说明 |
|---|---|---|
| `ingest` | `/ingest <路径>` 或 "摄取""导入资料" | 将 raw/ 原始资料编译到 wiki/，自动归档 |
| `query` | `/query <问题>` 或 "我的笔记里怎么说" | 检索本地 Wiki 并基于已有知识页回答 |
| `lint` | `/lint` 或 "检查知识库健康度" | 扫描死链、孤岛页面、索引完整性，只读报告 |
| `需求文档` | `/需求文档 <内容>` 或 "整理需求文档""生成需求文档" | 将任意形式输入（一句话/对话/文件/链接）整理为结构化需求文档，三步式：原始需求描述→需求分析（默认空）→实现部分，归档到 raw/00-requirement/ |

> 📌 `sync` 条目已于 2026-09-23 移除 —— `skills/sync/` 目录不存在（幽灵条目）。如后续恢复该技能，需重新登记。

### 数仓取数

| 技能 | 触发方式 | 说明 |
|---|---|---|
| `取数` | `/取数 <需求>` 或 "写取数 SQL""查哪个表" | 数仓取数需求 SQL 方法论，含 L1/L2/L3 证据分级 |
| `zhaoshanghui-member` | "查招商荟会员""会员数量/画像/手机号/城市/角色/注册登录/渠道" | 招商荟会员指标取数：`HD17_ONE_USER_BASIC_INFO_SS` 与 `hd17_one_user_inc_ss` 两表路由、字段证据坐标、取数 SQL 模板；只生成 SQL 与口径说明，不执行查询 |
| `sql-etl-review` | "提交 SQL""请求 Review""上线前检查""任务变慢""结果膨胀" | 按招商城科数仓规范评审 Hive/Spark SQL 与 T+1 离线 ETL；强制回答每张输入表、Join 后、目标表各一行代表什么 |
| `sql-formatter` | `/sql-format` 或 "格式化这段 SQL""美化 SQL""统一 SQL 风格" | SQL 格式化与风格统一 |

### 数据工程

| 技能 | 触发方式 | 说明 |
|---|---|---|
| `数据补数` | "补数据""回刷""补跑任务""手动触发" | 数据资产平台手动触发调度任务补数，逐日调用 runManualTask |
| `入湖` | `/入湖` 或 "生成入湖申请表""数据入湖 Excel" | 基于 `数据入湖申请表模版.xlsx` 生成结构化入湖申请 Excel（申请表单/填写说明/表结构说明三个 sheet） |

### 目录结构

```
skills/                          # 唯一真源
├── 取数/SKILL.md
├── sql-etl-review/SKILL.md
├── sql-formatter/SKILL.md
├── ingest/SKILL.md
├── lint/SKILL.md
├── query/SKILL.md
├── 需求文档/SKILL.md
├── 数据补数/SKILL.md
├── 入湖/SKILL.md
├── ...
├── .dsh/skills -> ../skills      # DSH 软链接（DSH 只认这条）
├── .codex/skills -> ../skills    # Codex 软链接
├── .workbuddy/skills -> ../skills
└── .claude/skills -> ../skills
```

## 页面 Frontmatter (YAML) 规范

所有生成的 wiki 页面必须包含以下 YAML 头部：

```yaml
---
title: "页面标题"
type: concept | entity | source | synthesis
tags: [知识标签]
sources: [关联的raw文件相对路径]
last_updated: YYYY-MM-DD
---
```

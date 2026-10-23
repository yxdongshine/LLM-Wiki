---
name: 数据补数
description: 在数据资产平台（dataasset-xc.cmft.com）手动触发指定调度任务补数，逐日调用 runManualTask 接口。适用于"补数据""跑漏了补一下""回刷某段时间数据""手动补跑任务"等场景。执行脚本为本 skill 自带的 backfill.py（支持 --start/--end/--task-id/--jwt/--cookie/--interval/--dry-run/--log），凭据从命令行参数或环境变量 DATA_ASSET_JWT / DATA_ASSET_COOKIE 读取，不在 skill 内硬编码。
tags: ["数据补数", "调度", "手动触发", "runManualTask", "数据资产平台"]
platforms: ["macOS"]
---

# 数据补数技能

## 功能说明

在数据资产平台 `https://dataasset-xc.cmft.com` 上，对指定调度任务按需手动补跑。核心是：**按业务需要生成日期清单 → 逐日调用 `runManualTask` 接口触发补数 → 检查返回状态**。

## 触发场景

- "补一下 5/17 到 5/22 的周数据"
- "这个任务上周漏跑了，回刷一下"
- "帮我补 1 月到 4 月每个月末的数据"
- "把某段时间的 xxx 任务补数"
- 用户提供"补数据/补跑/回刷/手动触发任务"等意图

## 关键依赖

**执行脚本：`skills/数据补数/backfill.py`（本 skill 自带，随 skill 一起分发，无外部依赖）。**

> ⚠️ 历史桌面脚本 `/Users/pengleicao/Desktop/supplement_data.py` 与 `get_weeklastday.py` **已删除**，不得再引用。原日期生成器能力已由本 skill 的日期清单逻辑替代（见第 2 步）。

`backfill.py` 能力清单：

| 参数 | 必填 | 说明 |
|---|---|---|
| `--start` | 是 | 开始日期 `YYYY-MM-DD` |
| `--end` | 是 | 结束日期 `YYYY-MM-DD`（含端点） |
| `--task-id` | 是 | 任务ID |
| `--project-id` | 是 | 项目ID |
| `--name` | 是 | 任务名 |
| `--jwt` | 是 | JwtToken，默认读环境变量 `DATA_ASSET_JWT` |
| `--cookie` | 是 | Authorization Cookie，默认读环境变量 `DATA_ASSET_COOKIE` |
| `--interval` | 否 | 每次间隔秒数，默认 `20`，**不得调小** |
| `--log` | 否 | 日志路径，默认 `~/Desktop/补数日志_<name>.log` |
| `--dry-run` | 否 | 只打印日期清单不执行，**全量前建议先跑一次** |

内置行为：

1. **日期生成**：`--start` ~ `--end` 逐日展开（**仅支持连续日期**）。
2. **触发**：逐日调 `/api/ops/circleTask/runManualTask`，`businessDateStart` 与 `businessDateEnd` 传同一日；固定头 `Login-Type: nuc`、`ProductKey: CyberData`，`env=5`（生产）、`tenantId=1001`、`userId=641`。
3. **成功判定**：响应含 `"code":"200"` 记成功，否则记失败。
4. **异常自停**：响应含 `"code":"1"` 或 `oauth` 字样（token 失效/登录跳转）→ **立即 `sys.exit(1)` 终止**，不再空转。
5. **收尾**：打印并落盘 `总计/成功/失败` 汇总 + 失败日期清单。

**周/月末模式注意**：`backfill.py` 只吃连续区间。补「每周日」或「每月末」时，需先自行算出日期清单，再用 curl 循环逐日触发（或改脚本支持 `--dates`，属功能变更，须先与主人确认）。

## 工作流

### 1. 确认补数需求（必须先问清，缺一不可）

**⚠️ 强制前置条件：每次补数，用户必须提供完整的 runManualTask 请求信息（否则不得执行）。** 引导用户提供 curl（可从浏览器开发者工具 / 平台接口直接复制），从 curl 中提取以下参数：

| 必填参数 | 说明 | curl 中的位置 |
|---|---|---|
| `name` | 任务名 | `--data-raw` 的 `"name"` |
| `taskId` | 任务ID | `--data-raw` 的 `"taskId"` |
| `projectId` / `projectIds` | 项目ID | `--data-raw` |
| `tenantId` | 租户ID | `--data-raw` |
| `userId` | 用户ID | `--data-raw` |
| `env` | 环境(5=生产) | `--data-raw` |
| `JwtToken` / `Cookie` | 认证凭据 | `-H 'JwtToken: ...'` / `-b '_a=...; Authorization=...'` |
| 日期范围 | 起止（`businessDateStart`/`businessDateEnd` 或用户口述） | `--data-raw` |

**两个来源**（都需拿到）：
1. **认证 + 任务标识**：完整 curl（含 `-H JwtToken`、`-b Cookie`、`--data-raw` 的 name/taskId/projectId）。
2. **补数日期**：用户口述区间 + 日期模式，或直接给出 `businessDateStart/End`。

> 交互范例：若用户只说"补月度数据"，必须追问"请提供该任务的 curl（含 name/taskId/projectId/token）以及补数日期范围"，拿到前不执行。

### 2. 生成补数计划（强制，先确认再执行）

**⚠️ 流程铁律：每次补数必须先输出「补数计划」，等用户明确确认后，才允许触发执行。绝不在未确认时直接补数。**

补数计划必须包含：

```
## 补数计划
- 任务: <name>
- 任务ID: <taskId>
- 日期范围: <YYYY-MM-DD> ~ <YYYY-MM-DD>
- 日期模式: 连续 / 每周日 / 每月末
- 待补日期清单: [d1, d2, ...]（共 N 个）
- 预计耗时: N × 20s ≈ X 分钟
- 已确认?: ⏳ 等待用户确认
```

- 生成日期清单（按日期模式选方式）：
```bash
# 连续日期：直接用 backfill.py，先 --dry-run 看清单
python3 skills/数据补数/backfill.py --dry-run --start 2026-05-17 --end 2026-05-22 \
  --task-id <ID> --project-id <PID> --name <NAME>

# 每周日：先算出范围内所有周日，再逐日 curl（backfill.py 不支持跳日）
# 每月末：先算出范围内每个月末，再逐日 curl
```

#### 确认闸门（硬性，不可跳过）

**「提供参数/范围/curl」≠「确认执行」。** 只有用户出现以下**明确确认措辞**之一，才允许触发补数：

- 明确说"确认补数"、"可以，执行"、"开始补"、"确认"、"就这么办，跑吧"
- 或明确指示某个日期开始执行（如"从 2026-01-31 开始"）

**以下情况一律视为未确认，必须停在计划展示阶段，不得执行：**
- 模糊指令："补数"、"补一下"、"跑吧"、"好"、"OK"（无明确执行指向）
- 只提供范围/curl/参数，未说执行
- 回答与计划无关的问题

**Agent 模式下的自我约束**：即使处于"你说我干"的主动执行模式，补数这类**生产环境高影响操作**也必须先展示计划并等明确确认，不得因模式倾向而跳过确认闸门。

- 若用户中途说"停止"，立即终止并汇报已触发到哪个日期。

### 3. 配置凭据（安全第一）

⚠️ **凭据（JwtToken、Cookie、userId）绝不在 skill 内硬编码，也不写入任何可被他人读取的文件。** 安全做法：

- **推荐**：`backfill.py` 已支持从环境变量读取，运行时临时注入即可，**不落盘**：
  ```bash
  DATA_ASSET_JWT='<jwt>' DATA_ASSET_COOKIE='<cookie>' \
    python3 skills/数据补数/backfill.py --start ... --end ... --task-id ... --project-id ... --name ...
  ```
- **或**：命令行 `--jwt` / `--cookie` 传参（注意会留在 shell history，敏感场景优先用环境变量）。
- **禁止**：把凭据写进 SKILL.md、wiki、docs 或任何提交到仓库的文件。

### 3.5 启动前预检 token（强制，防跨天失效）

**⚠️ 铁律：token 有时效，跨天/隔久后旧凭据可能已失效。启动新一轮补数前必须预检，不得直接全量跑旧 token。**

1. **主动确认时效**：若距上次成功补数已跨天或隔了很久，先提醒主人"旧 token 可能已过期，请提供新 curl（含新 JwtToken/Cookie）"，拿到新凭据再继续；不要赌旧 token 仍有效。
2. **单日预检（必做）**：正式全量前，先用当前凭据发 **1 次**单日请求验证：
   - 返回 `{"code":"200","msg":"成功"}` → token 有效，可全量。
   - 返回**登录跳转 URL**（如 `nuc-c.cmhk.com/oauth/...`）→ **token 失效**，立即停止，向主人要新凭据，**不得继续跑**。
3. **发现异常立即停 + 报告**：若全量中某个日期返回非 200/跳转，立即终止进程并报告，不让它空转（白等 20s × 剩余天数）。

### 4. 执行补数（说执行 = 当场调用工具）

**⚠️ 铁律：凡是承诺/宣布"启动、开始、执行"补数，必须在同一轮实际调用工具发起（Bash 后台任务 / 逐条 curl），绝不只输出文字声明而不触发工具调用。**

- **文字 ≠ 执行**：回复"已启动""开始补数""正在执行"之前，必须先真正发起工具调用（后台 Bash 拿到 task_id，或逐条发出 curl）。没有真实工具调用，就等于没执行。
- **立即启动，不跨轮**：用户确认后，**当轮**就要发出启动命令；不要先回复"启动中"再等下一轮才动手。多次出现"说了没启动"属严重失误。
- **启动后确认 task_id**：后台任务应返回 `task_id`，据此向用户确认"已真正启动 + 后台任务标识"，而不是笼统说"已在跑"。
- 执行方式（二选一，均需真实调用）：
  - **Python 脚本（连续日期首选）**：调本 skill 的 `backfill.py`，后台运行。
  - **curl 逐日**：写 shell 循环，`for BD in ...; do curl ...; sleep 20; done`，后台运行（跳日模式只能用这个）。

```bash
# 后台启动示例（curl 循环，59 天）
BDATES=(...); for BD in "${BDATES[@]}"; do RESP=$(curl -s ... --data-raw "{\"businessDateStart\":\"${BD}\",...}"); echo "$BD|$RESP"; sleep 20; done
```

```bash
# 后台启动示例（Python，连续日期）
DATA_ASSET_JWT='<jwt>' DATA_ASSET_COOKIE='<cookie>' \
/Users/pengleicao/.workbuddy/binaries/python/envs/default/bin/python \
  skills/数据补数/backfill.py \
  --start 2026-03-01 --end 2026-08-27 \
  --task-id <ID> --project-id <PID> --name <NAME> --interval 20
```

### 5. 检查结果

- 每个日期打印 `Status: 200` 即成功。
- 非 200 或抛异常 → 记录失败日期，重试或人工确认。
- 注意接口有 **20s 间隔**要求（避免资源抢占），不要缩短。

## 边界与注意事项

- **凭据敏感**：JWT/Cookie 属机密，仅通过环境变量或命令行临时传入。不扩散、不提交到仓库、不写入 wiki/文档/SKILL.md。
- **间隔控制**：`--interval` 默认 20s，是防资源抢占的下限，勿调小；大批量补数建议拉大间隔。
- **幂等**：重复触发同日期通常无害，但建议补数前先确认该日是否已补过，避免重复计算。
- **只补该任务**：不改动 `name/taskId/projectId` 以外参数，避免误触发其他任务。
- **跳日模式无脚本支持**：`backfill.py` 只处理连续区间；每周日/每月末需自行生成清单走 curl 循环。
- **联网依赖**：需能访问 `dataasset-xc.cmft.com`（内网/授权网络），如失败检查网络与 token 时效。
- **脚本路径**：`backfill.py` 随 skill 分发，引用时用相对 skill 根目录的路径，勿硬编码绝对路径。

## 完成标准

- ✅ 已从用户拿到完整 curl（含 JwtToken/Cookie/name/taskId/projectId）——**缺凭据或任务标识不得执行**。
- ✅ **已确认补数日期范围与日期模式（连续/每周日/每月末）**。
- ✅ **已输出「补数计划」并获用户明确确认**——未确认绝不执行。
- ✅ **token 已预检**——单日请求验证返回 200 成功（或已获主人提供的新凭据），非登录跳转。
- 已按正确模式生成日期清单。
- ✅ **已真正启动并确认**——后台任务已发出（拿到 task_id 或已发出逐条 curl），而非仅文字声明。
- 已安全复用凭据（未扩散、未硬编码到新文件）。
- 已逐日触发补数并核对返回状态，失败项已记录并提示。
- 已向用户汇报补数结果（成功/失败日期清单）。

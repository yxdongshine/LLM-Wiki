---
name: sql-formatter
description: SQL 格式化与风格统一工具。支持 `/sql-format`，也适用于"格式化这段 SQL""美化 SQL""统一 SQL 风格""帮我整理这个查询"等场景。覆盖 SELECT/JOIN/WHERE/GROUP BY/子查询/CTE/CASE WHEN/UNION 等全语法结构的格式化规则，输出风格统一、可读性强的 SQL。
user-invocable: true
---

# SQL Formatter：SQL 格式化与风格统一

## 目标

将用户提供的 SQL 语句格式化为**风格统一、层次清晰、易于阅读和维护**的规范 SQL，核心原则：**一致性优先于个人偏好，可读性优先于紧凑性**。

1. 统一关键字大小写、缩进、换行、逗号位置等基础格式。
2. 保持 SQL 语义完全不变，不修改任何逻辑、表名、字段名或条件。
3. 对子查询、CTE、JOIN、CASE WHEN、UNION 等复杂结构采用层次化缩进。
4. 仅格式化，不验证语法正确性，不修改表结构引用。
5. **唯一例外**：子查询 / CTE 中的 `SELECT *` 必须按第十五节展开为显式字段列表。这是本技能唯一允许的"新增元素"改写，优先级**高于**后文"禁止添加、删除或重排任何 SQL 元素"。除此之外不得增删任何 SQL 元素。

## 触发方式

- `/sql-format <SQL 文本>`
- "格式化这段 SQL"
- "美化这个查询"
- "帮我整理一下这个 SQL"
- "统一 SQL 风格"
- "把这个 SQL 格式化一下"

## 格式化规则

### 一、关键字规则

#### 1.1 SQL 关键字大写

所有 SQL 保留关键字统一使用 **UPPERCASE**（大写）：

```
SELECT, FROM, WHERE, AND, OR, NOT, IN, EXISTS, BETWEEN, LIKE, IS, NULL,
JOIN, INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, CROSS JOIN, ON,
GROUP BY, ORDER BY, ASC, DESC, HAVING, LIMIT, OFFSET,
UNION, UNION ALL, INTERSECT, EXCEPT,
INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, TRUNCATE,
CASE, WHEN, THEN, ELSE, END,
WITH, AS, DISTINCT, ALL, COUNT, SUM, AVG, MAX, MIN,
OVER, PARTITION BY, ROWS, RANGE, UNBOUNDED, PRECEDING, FOLLOWING, CURRENT ROW,
CAST, COALESCE, NULLIF, IFNULL, NVL,
TRUE, FALSE, INTO, VALUES, SET, DEFAULT
```

#### 1.2 函数名大写

内置函数名统一大写：

```
COUNT(), SUM(), AVG(), MAX(), MIN(), COALESCE(), CAST(), 
ROW_NUMBER(), RANK(), DENSE_RANK(), LAG(), LEAD(),
SUBSTR(), CONCAT(), UPPER(), LOWER(), TRIM(), LENGTH(),
DATE_FORMAT(), TO_DATE(), NOW(), CURRENT_DATE(), CURRENT_TIMESTAMP(),
NVL(), IFNULL(), NULLIF(), DECODE(),  
GET_JSON_OBJECT(), EXPLODE(), LATERAL VIEW
```

#### 1.3 表名/字段名/别名保持原样

- 表名、字段名、别名保持原始大小写（通常是小写或原始定义）。
- 不强制改写表名/字段名的大小写。

### 二、缩进规则

#### 2.1 基础缩进

使用 **4 个空格** 作为一级缩进，不使用 Tab 字符。

#### 2.2 顶层子句左对齐

以下顶层子句**不缩进**，顶格书写，与 SELECT 首字母对齐：

```
SELECT
FROM
WHERE
GROUP BY
HAVING
ORDER BY
LIMIT
```

> FROM 与 SELECT 首字母左对齐（同一缩进层级）。WHERE/AND 仍按尾字母对齐：WHERE 补 2 空格使 D 与 E 同列。

#### 2.3 SELECT 列缩进

`SELECT` 后的每个列表达式缩进一级（4 空格），列之间用换行分隔，逗号紧贴字段名（逗号后无空格）。

#### 2.4 SELECT 四列对齐

字段表达式、`AS`、别名、`--` 注释四列对齐，按最长元素预留空格。**首个字段补一个空格（模拟逗号位），确保所有字段表达式首字对齐：**

```sql
SELECT
     ap.id                           AS    id                  -- 主键id
    ,ap.user_id                      AS    one_user_id         -- 用户id
    ,ap.nickname                     AS    nickname            -- 昵称
    ,ap.avatar                       AS    avatar              -- 头像
    ,oub.mobile_prefix               AS    mobile_prefix       -- 手机区号
    ,oub.mobile                      AS    mobile              -- 手机号码
    ,NVL(t1.cert_type, ext1)         AS    cert_type           -- 证件类型
    ,NVL(t1.cert_no, certificate_no) AS    cert_no             -- 证件号码
    ,NVL(t1.cert_name, last_name)    AS    cert_name           -- 证件姓名
FROM source_table
WHERE stat_date = '2025-01-01'
```

对齐规则：
- 第1列：字段表达式，首个字段补 1 空格（补偿逗号位），后续字段 `,` 占 1 字符，所有表达式首字对齐
- 第2列：`AS` 关键字，统一对齐
- 第3列：别名，按最长别名对齐，之间至少 1 空格
- 第4列：`--` 注释，按最长别名后对齐，之间至少 2 空格

#### 2.5 列别名

- 使用 `AS` 关键字明确别名（推荐，不强制）。
- 别名与列表达式在同一行。

### 三、逗号规则

使用**前置逗号**（leading comma）风格，逗号在列表达式之前，逗号后紧跟字段名（无空格）：

```sql
SELECT
     one_userid
    ,user_name
    ,point_balance
    ,total_consume
FROM point_table
```

**优点**：新增/删除列时只影响一行，diff 清晰；减少遗漏逗号的语法错误。

### 四、FROM / JOIN 规则

#### 4.1 FROM 子句

`FROM` 后跟表名（可含库名），表别名使用简写：

```sql
FROM dwd.point_detail p
INNER JOIN dim.user_info u
  ON p.one_userid = u.one_userid
```

#### 4.2 JOIN 缩进

- `JOIN` 关键字与 `FROM` 对齐（顶格）。
- `ON` 和 `AND` 与 `JOIN` **尾字母对齐**：JOIN 4 字符（N 在第 4 列），ON 2 字符（补 2 空格，N 在第 4 列），AND 3 字符（补 1 空格，D 在第 4 列）。

```sql
FROM dwd.point_detail p
INNER JOIN dim.user_info u
  ON p.one_userid = u.one_userid
 AND u.stat_date = '2025-01-01'
LEFT JOIN dim.city_info c
  ON u.city_code = c.city_code
```

#### 4.3 多个 ON 条件

每个 `AND`/`OR` 条件单独一行，与 `JOIN` 尾字母对齐：

```sql
LEFT JOIN dim.user_tag t
  ON u.one_userid = t.one_userid
 AND t.tag_type = '会员等级'
 AND t.stat_date = '2025-01-01'
```

#### 4.4 子查询作为 JOIN 对象

子查询用括号包裹，缩进按子查询规则处理：

```sql
LEFT JOIN (
    SELECT
        one_userid
        , MAX(point_balance) AS max_balance
    FROM dwd.point_balance
    WHERE stat_date = '2025-01-01'
    GROUP BY one_userid
) b
  ON u.one_userid = b.one_userid
```

### 五、WHERE 规则

#### 5.1 条件换行

`WHERE` 后每个条件单独一行，`AND`/`OR` 与 `WHERE` **尾字母对齐**：WHERE 5 字符（E 在第 5 列），AND 3 字符（补 2 空格，D 在第 5 列）。

```sql
WHERE stat_date = '2025-01-01'
  AND point_type = '发放'
  AND amount > 0
  AND status IN ('已结算', '待结算')
```

#### 5.2 IN 列表

- 少量值（≤5个）可放同一行。
- 较多值（>5个）每个值单独一行，前置逗号：

```sql
WHERE city_code IN (
    'SZ'
    ,'BJ'
    ,'SH'
    ,'GZ'
    ,'CD'
)
```

#### 5.3 子查询嵌套

WHERE 中的子查询保持缩进层次：

```sql
WHERE one_userid IN (
    SELECT DISTINCT one_userid
    FROM dim.active_user
    WHERE stat_date = '2025-01-01'
)
  AND point_type = '发放'
```

### 六、GROUP BY / ORDER BY 规则

#### 6.1 GROUP BY

每个分组字段单独一行，前置逗号：

```sql
GROUP BY
     city_code
    ,point_type
    ,stat_date
```

#### 6.2 ORDER BY

每个排序列单独一行，前置逗号，`ASC`/`DESC` 明确写出：
```sql
ORDER BY
     stat_date DESC
    ,city_code ASC
    ,total_amount DESC
```

#### 6.3 HAVING

`HAVING` 条件格式与 `WHERE` 一致：

```sql
HAVING COUNT(DISTINCT one_userid) > 100
  AND SUM(point_amount) > 10000
```

### 七、子查询规则

#### 7.1 嵌套子查询

每层子查询缩进一级（4 空格），括号独立一行：

```sql
SELECT
    one_userid
    ,total_points
FROM (
        SELECT
            one_userid
            ,SUM(point_amount) AS total_points
        FROM (
                SELECT
                    one_userid
                    ,point_amount
                FROM dwd.point_detail
                WHERE stat_date >= '2025-01-01'
        			) detail
        GROUP BY one_userid
			) agg
WHERE total_points > 1000
```

#### 7.2 括号对齐

- 左括号 `(` 在子查询开始行，或根据上下文灵活放置。
- 右括号 `)` 与子查询别名在同一行，顶格或与父查询对齐。

### 八、CTE（WITH 子句）规则

#### 8.1 基本格式

```sql
WITH cte_name AS (
    SELECT
        one_userid
        ,SUM(point_amount) AS total_points
    FROM dwd.point_detail
    WHERE stat_date = '2025-01-01'
    GROUP BY one_userid
)

SELECT
     u.one_userid
    ,u.user_name
    ,cte.total_points
FROM dim.user_info u
INNER JOIN cte_name cte
  ON u.one_userid = cte.one_userid
```

#### 8.2 多个 CTE

每个 CTE 之间用逗号分隔，前置逗号风格：

```sql
WITH point_summary AS (
    SELECT
        one_userid
        ,SUM(point_amount) AS total_points
    FROM dwd.point_detail
    WHERE stat_date = '2025-01-01'
    GROUP BY one_userid
)

,active_users AS (
    SELECT DISTINCT one_userid
    FROM dwd.login_log
    WHERE stat_date = '2025-01-01'
)

SELECT
    p.one_userid
    ,p.total_points
FROM point_summary p
INNER JOIN active_users a
  ON p.one_userid = a.one_userid
```
### 九、CASE WHEN 规则

```sql
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    WHEN condition3 THEN result3
    ELSE default_result
END AS alias_name
```

- `CASE` 和 `END` 首字母对齐。当 CASE 前有逗号（`,CASE`）时，`END` 补 1 空格对齐 CASE 的首字母 `C`。**注意：END 后的空格需相应减少 1 个，以保持 `AS` 列与其他行对齐。**
- 每个 `WHEN ... THEN ...` 缩进一级。
- `ELSE` 与 `WHEN` 对齐。
- 嵌套 CASE 每层额外缩进一级。

```sql
SELECT
    one_userid
    ,CASE
        WHEN point_balance >= 10000 THEN '高余额'
        WHEN point_balance >= 5000 THEN '中余额'
        WHEN point_balance > 0 THEN '低余额'
        ELSE '零余额'
     END AS balance_level
    ,CASE
        WHEN city_code IN ('SZ', 'GZ') THEN
            CASE
                WHEN point_balance >= 10000 THEN '一线-高'
                ELSE '一线-低'
            END
        ELSE '其他'
     END AS city_balance_level
FROM dwd.point_balance
```

### 十、UNION / UNION ALL 规则

```sql
SELECT
    one_userid
    ,point_amount
FROM dwd.point_issue
WHERE stat_date = '2025-01-01'

UNION ALL

SELECT
    one_userid
    ,point_amount
FROM dwd.point_recycle
WHERE stat_date = '2025-01-01'
```

- `UNION` / `UNION ALL` 前后各空一行。
- 每个 SELECT 块独立格式化。

### 十一、窗口函数规则

```sql
SELECT
    one_userid
    ,stat_date
    ,point_amount
    ,ROW_NUMBER() OVER (
        PARTITION BY one_userid
        ORDER BY stat_date DESC
    ) AS rn
    ,SUM(point_amount) OVER (
        PARTITION BY one_userid
        ORDER BY stat_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_points
FROM dwd.point_detail
```

- 简单窗口函数（仅 `PARTITION BY`，无 `ORDER BY`/`ROWS`）放一行：`COUNT(1) OVER (PARTITION BY user_id)`。
- 含 `ORDER BY` 或 `ROWS` 时换行，`PARTITION BY` 和 `ORDER BY` 缩进一级。
- 窗口帧子句 `ROWS BETWEEN ... AND ...` 与 `ORDER BY` 对齐。

### 十二、注释规则

#### 12.1 行内注释

```sql
SELECT
    one_userid       -- 用户ID
    ,point_balance   -- 余额，单位：荟豆
FROM dwd.point_balance
```

注释使用 `--`，与代码之间至少两个空格。

#### 12.2 块注释

```sql
/*
 * 查询用户余额分层统计
 * 作者：xxx
 * 日期：2025-01-01
 */
```

```sql
SELECT
    one_userid
    ,CASE
        WHEN point_balance >= 10000 THEN '高余额'
        ELSE '低余额'
    END AS balance_level
FROM dwd.point_balance
```
#### 12.3 分段注释

复杂 SQL 用注释分隔逻辑段落：

```sql
-- ============================================================
-- Step 1: 获取活跃用户
-- ============================================================
WITH active_users AS (
    ...
)

-- ============================================================
-- Step 2: 关联积分明细
-- ============================================================
SELECT ...
```

### 十三、DDL（CREATE TABLE）规则

> **注释块内的 DDL 同样要格式化。** 被 `--` 注释掉的建表语句（脚本头部常见的表结构说明块）按本节规则重排字段名/类型/COMMENT 三列对齐，每行保留 `-- ` 前缀。第 12.1 节注释规则中的「禁止修改注释内容」指的是注释的**语义内容**（文字、口径、字段说明文字）不得改动；注释块内 **DDL 代码的排版格式**不属于「注释内容」，必须格式化。

#### 13.1 建表语句格式

```sql
CREATE TABLE db.table_name (
    field_name1    STRING  COMMENT '字段备注1'
    ,field_name2   BIGINT  COMMENT '字段备注2'
    ,field_name3   DECIMAL(18, 4) COMMENT '字段备注3'
    ,field_name4   INT     COMMENT '字段备注4'
)
COMMENT '表备注'
PARTITION BY (stat_date STRING COMMENT '统计日期')
STORED AS ORC
;
```

#### 13.2 对齐规则

- 字段名、类型、COMMENT 三列对齐，使用空格填充使同类元素对齐。
- 字段名按最长字段名对齐，类型按最长类型对齐，COMMENT 关键字对齐。
- 前置逗号，逗号后紧跟字段名（无空格）。
- 括号独立一行，`CREATE TABLE` 和 `)` 顶格。
- 字段列表缩进一级（4 空格）。

#### 13.3 多列对齐示例

```sql
CREATE TABLE dwd.point_detail (
    one_userid          STRING          COMMENT '用户ID'
    ,stat_date          STRING          COMMENT '统计日期'
    ,point_type         STRING          COMMENT '积分类型：发放/回收/过期'
    ,point_amount       DECIMAL(18, 4)  COMMENT '积分金额'
    ,point_balance      DECIMAL(18, 4)  COMMENT '积分余额'
    ,create_time        STRING          COMMENT '创建时间'
    ,update_time        STRING          COMMENT '更新时间'
)
COMMENT '积分明细表'
PARTITION BY (stat_date STRING COMMENT '统计日期')
STORED AS ORC
;
```

### 十四、其他规则

#### 13.1 运算符空格

运算符两侧各加一个空格：

```sql
a = b
a > b
a >= b
a + b
a || b
```

#### 13.2 括号内空格

- 左括号后不加空格。
- 右括号前不加空格。
- 函数调用括号紧贴函数名：`COUNT(*)`、`SUM(amount)`。

#### 13.3 空行

- 顶层子句之间不加空行（SELECT / FROM / WHERE / GROUP BY / HAVING / ORDER BY 紧密连接）。
- CTE 定义之间空一行。
- UNION 前后各空一行。
- 可选：复杂查询的逻辑段落之间加空行。

#### 13.4 长行处理

单行超过 120 字符时换行：

- 列表达式过长：将表达式拆到下一行，缩进一级。
- 函数参数过多：每个参数单独一行。
- 字符串过长：不做截断，允许超出。

```sql
SELECT
    one_userid
    ,CONCAT(
        COALESCE(province_name, '未知')
        ,'-'
        ,COALESCE(city_name, '未知')
        ,'-'
        ,COALESCE(district_name, '未知')
    ) AS full_address
FROM dim.user_address
```

### 十五、SELECT * 展开规则（本节优先级最高）

**禁止在子查询和 CTE 中使用 `SELECT *`，必须展开为显式字段列表。**

本节是全文唯一允许"新增 SQL 元素"的规则，与"禁止添加、删除或重排任何 SQL 元素"冲突时，**以本节为准**。展开属语义等价改写，不视为"修改 SQL 逻辑"。

#### 15.1 展开粒度：收窄到实际引用字段

**只列出被用到的字段，不列该表全部字段。**

字段集合 = 以下两类字段的并集：

1. **外层引用字段**：子查询/CTE 的外层 SELECT、JOIN ON、WHERE、GROUP BY、HAVING、ORDER BY 中通过该别名引用的字段（如 `b.m_date_code` → `m_date_code`）。
2. **子查询自身引用字段**：该子查询自己的 WHERE / GROUP BY / ORDER BY / PARTITION BY 中用到的字段。

排除项：

- 既不被外层引用、也不被子查询自身引用的字段，一律不列。
- `COUNT(*)` 中的 `*` 不受此规则约束。

#### 15.2 字段名的证据来源（按优先级，禁止猜测）

展开前必须按以下顺序取得字段名，**字段名只能来自实际可见的文本，不得靠"这类表一般有 X 字段"补全**：

| 优先级 | 来源 | 说明 |
|---|---|---|
| 1 | **同文件内的 CTE 定义** | 若 `*` 引用的对象是本文件内定义的 CTE，直接取其 SELECT 列表中的字段名与别名（含 `AS` 后的别名）。这是最强证据。 |
| 2 | **同文件内已出现的字段引用** | 外层查询里写出的 `别名.字段名`，本身就是字段存在的证据。 |
| 3 | **项目 `raw/` 或 `wiki/` 中该表的 DDL / 字段清单** | 表为物理表且同文件内无字段信息时，到项目资料中查找建表语句或字段清单。 |

#### 15.3 降级规则（证据不足时）

若上述三级来源**均无法**确定字段名（物理表且项目内无 DDL），则：

1. **保留该处 `SELECT *` 不动**，不要凭表名、命名习惯或同类表推测字段。
2. 在格式化结果**末尾**追加"待展开清单"，逐条列出：

```sql
-- ============================================================
-- 待展开清单（SELECT * 无法展开：缺字段证据）
-- ============================================================
-- 位置：<外层别名> 子查询，FROM <表名>
-- 原因：该表在项目资料中无 DDL / 字段清单
-- 待办：确认字段后手动展开为显式字段列表
```

3. 在交付说明中告知用户哪几处未展开及原因。

**留白优于编造**：宁可保留 `*` 并明确报告，也不得写入未经证实的字段名。

#### 15.4 示例

**格式化前：**
```sql
WITH dim_date_temp AS (
    SELECT m_date_code, m_year, m_week_1_7_code, m_week_1_7_name, extra_col
    FROM dwd_cmsk.hd00_date_dim_cs
)
SELECT
    b.m_week_1_7_code,
    b.m_year,
    b.m_week_1_7_name
FROM some_table a
INNER JOIN (
    SELECT *
    FROM dim_date_temp
    WHERE m_date_code = '2025-01-01'
) b
    ON a.db_date = b.m_date_code
```

**格式化后**（`m_date_code` 来自外层 ON 与子查询 WHERE，`extra_col` 未被引用故剔除）：
```sql
WITH dim_date_temp AS (
    SELECT
         m_date_code
        ,m_year
        ,m_week_1_7_code
        ,m_week_1_7_name
        ,extra_col
    FROM dwd_cmsk.hd00_date_dim_cs
)

SELECT
     b.m_week_1_7_code
    ,b.m_year
    ,b.m_week_1_7_name
FROM some_table a
INNER JOIN (
    SELECT
         m_date_code
        ,m_year
        ,m_week_1_7_code
        ,m_week_1_7_name
    FROM dim_date_temp
    WHERE m_date_code = '2025-01-01'
) b
    ON a.db_date = b.m_date_code
```

> 注意：CTE 定义自身的 `SELECT` 列**不因外层少引用而删减**——只展开 `*`，不改写已有的显式列清单。

## 格式化流程

### 1. 接收 SQL

接收用户提供的 SQL 文本，可以是完整的 SELECT/INSERT/CREATE 语句或片段。

### 2. 分析结构

识别 SQL 中的顶层子句、子查询层级、JOIN 关系、CTE 定义等结构。

### 3. 应用规则

按上述规则逐层格式化：
1. 关键字/函数名大写
2. 缩进层次化
3. 逗号前置化
4. 子句换行
5. 注释对齐

### 4. 输出

输出格式化后的 SQL，不附带多余解释（除非用户明确要求说明修改点）。

## 格式化示例

### 示例 1：基础 SELECT

**输入：**
```sql
select one_userid,user_name,point_balance,sum(point_amount) total from dwd.point_detail where stat_date='2025-01-01' group by one_userid,user_name,point_balance order by total desc limit 100
```

**输出：**
```sql
SELECT
    one_userid
    ,user_name
    ,point_balance
    ,SUM(point_amount) AS total
FROM dwd.point_detail
WHERE stat_date = '2025-01-01'
GROUP BY
    one_userid
    ,user_name
    ,point_balance
ORDER BY
    total DESC
LIMIT 100
```

### 示例 2：多表 JOIN

```sql
select p.one_userid,u.user_name,c.city_name,sum(p.point_amount) as total_points from dwd.point_detail p inner join dim.user_info u on p.one_userid = u.one_userid left join dim.city_info c on u.city_code = c.city_code where p.stat_date between '2025-01-01' and '2025-01-31' and p.point_type = '发放' group by p.one_userid,u.user_name,c.city_name having sum(p.point_amount) > 1000 order by total_points desc
```

**输出：**
```sql
SELECT
    p.one_userid
    ,u.user_name
    ,c.city_name
    ,SUM(p.point_amount) AS total_points
FROM dwd.point_detail p
INNER JOIN dim.user_info u
  ON p.one_userid = u.one_userid
LEFT JOIN dim.city_info c
  ON u.city_code = c.city_code
WHERE p.stat_date BETWEEN '2025-01-01' AND '2025-01-31'
  AND p.point_type = '发放'
GROUP BY
    p.one_userid
    ,u.user_name
    ,c.city_name
HAVING SUM(p.point_amount) > 1000
ORDER BY
    total_points DESC
```
### 示例 3：CTE + 子查询

**输入：**
```sql
with summary as (select one_userid,sum(point_amount) total from dwd.point_detail where stat_date='2025-01-01' group by one_userid) select u.one_userid,u.user_name,s.total,case when s.total >= 10000 then '高' when s.total >= 5000 then '中' else '低' end as level from dim.user_info u left join summary s on u.one_userid = s.one_userid where u.stat_date='2025-01-01' order by s.total desc
```

**输出：**
```sql
WITH summary AS (
    SELECT
        one_userid
        ,SUM(point_amount) AS total
    FROM dwd.point_detail
    WHERE stat_date = '2025-01-01'
    GROUP BY one_userid
)

SELECT
    u.one_userid
    ,u.user_name
    ,s.total
    ,CASE
        WHEN s.total >= 10000 THEN '高'
        WHEN s.total >= 5000 THEN '中'
        ELSE '低'
    END AS level
FROM dim.user_info u
LEFT JOIN summary s
    ON u.one_userid = s.one_userid
WHERE u.stat_date = '2025-01-01'
ORDER BY
    s.total DESC
```

**输入：**
```sql
select one_userid,point_amount,'issue' as type from dwd.point_issue where stat_date='2025-01-01' union all select one_userid,point_amount,'recycle' as type from dwd.point_recycle where stat_date='2025-01-01' order by one_userid,type
```

**输出：**
```sql
SELECT
    one_userid
    ,point_amount
    ,'issue' AS type
FROM dwd.point_issue
WHERE stat_date = '2025-01-01'

UNION ALL

SELECT
    one_userid
    ,point_amount
    ,'recycle' AS type
FROM dwd.point_recycle
WHERE stat_date = '2025-01-01'

ORDER BY
    one_userid
    ,type
```
### 示例 5：窗口函数

**输入：**
```sql
select one_userid,stat_date,point_amount,row_number() over(partition by one_userid order by stat_date desc) as rn,sum(point_amount) over(partition by one_userid order by stat_date rows between unbounded preceding and current row) as cum from dwd.point_detail where stat_date>='2025-01-01'
```

**输出：**
```sql
SELECT
    one_userid
    ,stat_date
    ,point_amount
    ,ROW_NUMBER() OVER (
        PARTITION BY one_userid
        ORDER BY stat_date DESC
    ) AS rn
    ,SUM(point_amount) OVER (
        PARTITION BY one_userid
        ORDER BY stat_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cum
FROM dwd.point_detail
WHERE stat_date >= '2025-01-01'
```

本格式化规则采用以下风格约定（与企业级数仓 SQL 风格一致）：

| 规则项 | 选择 | 备选方案 |
|--------|------|----------|
| 关键字大小写 | UPPERCASE | lowercase |
| 缩进宽度 | 4 空格 | 2 空格 |
| 逗号位置 | 前置逗号，逗号后紧跟字段名（无空格） | 后置逗号，逗号后空格 |
| SELECT 对齐 | 表达式/as/别名/注释 四列对齐 | 不强制对齐 |
| JOIN 缩进 | 顶格（与 FROM 对齐） | 缩进一级 |
| 别名关键字 | 使用 `AS` | 省略 `AS` |
| ON/AND 缩进 | 与 JOIN 尾字母对齐（ON 2空格，AND 1空格） | 缩进一级（4 空格） |
| FROM 对齐 | 与 SELECT 首字母左对齐 | 尾字母对齐 |
| WHERE AND 对齐 | 与 WHERE 尾字母对齐（2 空格） | 缩进一级（4 空格） |
| CASE/END 对齐 | 尾字母对齐（END 补1空格补偿逗号位） | 左对齐 |
| DDL 字段对齐 | 字段名/类型/COMMENT 三列对齐 | 不强制对齐 |
当用户明确指定风格偏好时，优先遵循用户指定的风格。否则使用本规则默认风格。

## 禁止事项

- **禁止**修改 SQL 逻辑、表名、字段名、条件值。
- **禁止**添加、删除或重排任何 SQL 元素（**唯一例外**：第十五节的子查询 / CTE `SELECT *` 展开）。
- **禁止**擅自"优化"或"改写" SQL 语句（如将子查询改写为 JOIN）。
- **禁止**修改注释内容。
- **禁止**在用户未要求时附带冗长的解释说明。
- **禁止**修改字符串字面量的大小写。
- **禁止**在子查询和 CTE 中保留 `SELECT *`，必须按第十五节展开为显式字段列表（`COUNT(*)` 除外）。
- **禁止**在字段名证据不足时推测字段并写入展开结果；此时应保留 `*` 并列入"待展开清单"。

## 完成标准

- 所有 SQL 关键字已转为大写。
- 缩进层次清晰，子查询、JOIN、CTE 层级分明。
- 逗号风格统一（前置逗号）。
- 每个列/条件/分组字段独占一行。
- **已执行 `SELECT *` 自检**：对输出全文检索 `SELECT *`（不含 `COUNT(*)`），确认子查询 / CTE 内出现次数为 **0**；每处展开记录字段名来源（同文件 CTE / 同文件引用 / 项目资料 DDL）。
- 若有因缺字段证据而保留的 `SELECT *`，已在输出末尾附"待展开清单"，并在交付说明中列出位置与原因。
- 每条展开后的字段名均可追溯到实际可见文本，无推测字段。
- SQL 语义与输入完全一致，无任何逻辑变更（`SELECT *` 展开除外）。
- 输出仅包含格式化后的 SQL（除非用户要求解释）。

## 交付前自检清单

输出前逐项确认，任一不通过则修正后重出：

| 检查项 | 方法 | 通过标准 |
|---|---|---|
| 无遗漏 `SELECT *` | 检索 `SELECT *` | 子查询/CTE 内 0 处 |
| 无推测字段 | 逐个核对字段名来源 | 每个字段名都能指到可见文本 |
| 无多余字段 | 比对字段集与引用集 | 不出现未被引用的字段 |
| `COUNT(*)` 未被误改 | 检索 `COUNT(*)` | 数量与输入一致 |
| 降级已声明 | 检查输出末尾 | 有未展开项则附清单 |
| 语义未变 | 比对表名/条件/逻辑 | 除 `*` 展开外无差异 |
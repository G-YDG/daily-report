---
name: daily-report
description: 生成工作日报。当用户说"生成日报"、"写日报"、"今天的日报"、"帮我写工作日报"、"生成今日工作总结"时触发。扫描代码主目录下所有 git 仓库的当日提交记录，生成结构化的中文 Markdown 日报文件。即使用户只是提到"日报"或"工作总结"，也应该使用此技能。
---

# 日报生成技能

扫描代码主目录下所有 git 仓库的提交记录，生成按项目分组的中文 Markdown 日报。

## 执行步骤

### 第一步：确定代码主目录

读取技能配置：

```bash
python3 ~/.claude/skills/daily-report/scripts/config.py get[config.py](scripts/config.py)
```

如果配置中已有 `root` 字段，直接使用。如果没有，主动询问用户："请提供代码主目录路径（如 `D:/Develop`），我会扫描该目录下所有 git 仓库。" 拿到后保存：

```bash
python3 ~/.claude/skills/daily-report/scripts/config.py set --root <用户提供的路径>
```

如果用户在请求中已经提供了主目录路径，直接保存并使用，不要重复询问。

### 第二步：收集数据

运行采集脚本，一次性获取所有仓库的提交记录：

```bash
python3 ~/.claude/skills/daily-report/scripts/collect_data.py --date YYYY-MM-DD --root <主目录>
```

**关键参数说明：**

- `--date`：目标日期（默认今天，由调用方指定）
- `--root`：代码主目录
- `--author`：作者过滤策略
  - 默认 `auto`：使用 `git config --global user.name`，过滤掉 codeup 等机器人提交
  - `all`：不过滤，保留所有作者
  - 具体字符串：按该字符串过滤
- `--jobs`：并行 git log 的并发数（默认 16）

脚本输出 JSON 结构：

```json
{
  "date": "2026-04-23",
  "root": "D:/Develop",
  "author_filter": "Ydg",
  "repos_scanned": 63,
  "projects": [
    {
      "path": "D:\\Develop\\Demo",
      "name": "demo",
      "commits": [{"hash": "5d831f9", "author": "Ydg", "subject": "..."}]
    }
  ]
}
```

只有 `commits` 非空的项目才会出现在 `projects` 数组中。

### 第三步：生成日报

按以下结构生成 Markdown：

```markdown
# 工作日报 - YYYY年MM月DD日

> 扫描了 N 个 git 仓库，其中 M 个有当日记录。

## {项目名 1}

- [模块/功能]：从该项目的 commit 中提炼出的工作内容摘要
- ...

## {项目名 2}

...

---
```

**内容生成原则：**

- **按项目分组**：每个有记录的项目独立成节，便于多仓库并行工作的展示，如果 README.md 有项目名称，优先使用该名称
- **提炼而非罗列**：项目下的条目要从 commit message 中提炼有意义的工作条目，而不是机械复制
- **conventional commits 归类**：如果该项目的 commit 使用了 feat/fix/refactor 等前缀，可按功能开发/问题修复/优化改进等类别组织条目顺序
- **空数据**：如果所有仓库当天都没有记录，输出："今日（YYYY-MM-DD）扫描了 N 个仓库，未找到任何提交记录。"

### 第四步：保存日报

读取配置中的 `report_dir`，如果未配置则默认保存到主目录下的 `daily-reports/`：

```
{主目录}/daily-reports/YYYY-MM-DD.md
```

如果目录不存在，先创建。保存后告知用户文件路径。

## 注意事项

- **性能**：默认 16 路并行扫描，60+ 仓库通常在 2 秒内完成
- **路径分隔符**：Windows 路径在 JSON 中会显示为 `\\`，写入日报时保持原样或转换为 `/` 都可以
- **指定日期**：用户说"昨天的日报"、"上周三的日报"等，转换为具体日期再传入脚本
- **commit hash**：脚本输出的 hash 已截断为 7 位

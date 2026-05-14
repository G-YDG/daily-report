# daily-report

扫描代码主目录下所有 git 仓库的提交记录，结合 Claude Code 会话摘要，生成结构化的中文 Markdown 日报。

## 功能特性

- 📦 自动扫描指定目录下所有 git 仓库
- 📊 收集指定日期的 commit 记录（支持作者过滤）
- 💬 关联 Claude Code 会话摘要
- 📝 生成按项目分组的 Markdown 日报

## 项目结构

```
daily-report/
├── scripts/
│   ├── collect_data.py    # 数据采集脚本
│   └── config.py          # 配置管理脚本
├── config.json            # 默认配置
└── SKILL.md               # 技能说明文档
```

## 使用方法

### 1. 配置代码主目录

```bash
# 查看当前配置
python3 scripts/config.py get

# 设置代码主目录
python3 scripts/config.py set --root D:/Develop

# 设置日报输出目录（可选）
python3 scripts/config.py set --report-dir D:/Develop/reports
```

### 2. 收集数据并生成日报

```bash
# 收集今天的数据
python3 scripts/collect_data.py --date $(date +%Y-%m-%d) --root D:/Develop

# 指定日期和作者过滤
python3 scripts/collect_data.py \
  --date 2026-05-14 \
  --root D:/Develop \
  --author auto \
  --max-depth 5
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--date` | 目标日期（格式：YYYY-MM-DD） | 必填 |
| `--root` | 代码主目录 | 必填 |
| `--max-depth` | 最大扫描深度 | 5 |
| `--author` | 作者过滤：`auto`(git config) / `all`(不过滤) / 具体字符串 | auto |

## 输出示例

```json
{
  "date": "2026-05-14",
  "root": "D:/Develop",
  "author_filter": "Ydg",
  "repos_scanned": 63,
  "projects": [
    {
      "path": "D:\\Develop\\Demo",
      "name": "demo",
      "commits": [{"hash": "5d831f9", "author": "Ydg", "subject": "feat: add new feature"}],
      "sessions": [{"time": "10:39", "summary": "优化代码结构", "is_summary": true}]
    }
  ]
}
```

## 技术细节

- **时间处理**：会话时间戳自动从 UTC 转换为 UTC+8
- **跳过目录**：自动跳过 `node_modules`、`.git`、`dist` 等无关目录
- **性能优化**：扫描 60+ 仓库通常在 10 秒内完成

## 依赖

- Python 3.8+
- Git（需在 PATH 中）

## 许可证

MIT
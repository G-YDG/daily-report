#!/usr/bin/env python3
"""
收集指定主目录下所有 git 仓库的提交记录。
用法: python3 collect_data.py --date YYYY-MM-DD --root D:/Develop
"""
import argparse
import functools
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

# 扫描时跳过的目录
SKIP_DIRS = {
    'node_modules', 'vendor', '.git', '.svn', '.hg',
    'dist', 'build', 'target', 'out', '.next', '.nuxt',
    '__pycache__', '.venv', 'venv', 'env',
    '.idea', '.vscode', '.cache',
}

# 并行 git log 的默认并发数
DEFAULT_JOBS = 16


def find_git_repos(root: str, max_depth: int = 5) -> list[str]:
    """递归找出指定目录下所有 git 仓库（含 .git 子目录的目录）。"""
    repos = []
    root_path = Path(root).resolve()

    def scan(path: Path, depth: int):
        if depth > max_depth:
            return
        if path.name in SKIP_DIRS:
            return
        # 当前目录是 git 仓库 -> 记录后不再深入
        if (path / '.git').exists():
            repos.append(str(path))
            return
        try:
            entries = list(path.iterdir())
        except (PermissionError, OSError):
            return
        for entry in entries:
            if entry.is_dir():
                scan(entry, depth + 1)

    scan(root_path, 0)
    return sorted(repos)


def get_git_user_name() -> str | None:
    """读取全局 git config 中的 user.name。"""
    try:
        result = subprocess.run(
            ['git', 'config', '--global', 'user.name'],
            capture_output=True, timeout=5,
        )
        if result.returncode == 0:
            name = result.stdout.decode('utf-8', errors='replace').strip()
            return name or None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

def collect_git_log(repo: str, date_str: str, author: str | None = None) -> list[dict]:
    """收集仓库当天的提交记录（不含 merge 提交）。可选按作者过滤。"""
    start = f"{date_str} 00:00:00"
    end = f"{date_str} 23:59:59"
    cmd = ['git', 'log', f'--after={start}', f'--before={end}',
           '--pretty=format:%h|%an|%s', '--no-merges']
    if author:
        cmd.append(f'--author={author}')
    try:
        result = subprocess.run(
            cmd, cwd=repo, capture_output=True, timeout=15,
        )
        if result.returncode != 0:
            return []
        stdout = result.stdout.decode('utf-8', errors='replace')
        commits = []
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 2)
            if len(parts) == 3:
                short_hash, commit_author, subject = parts
                commits.append({
                    'hash': short_hash[:7],
                    'author': commit_author,
                    'subject': subject,
                })
        return commits
    except (subprocess.TimeoutExpired, OSError):
        return []

def main():
    parser = argparse.ArgumentParser(description='收集多仓库 git log')
    parser.add_argument('--date', required=True, help='日期，格式 YYYY-MM-DD')
    parser.add_argument('--root', required=True, help='代码主目录，如 D:/Develop')
    parser.add_argument('--max-depth', type=int, default=5, help='最大扫描深度（默认 5）')
    parser.add_argument('--author', default=None,
                        help='按作者过滤提交。传 "auto" 使用 git config user.name；传 "all" 不过滤；'
                             '传具体字符串则按该字符串过滤。默认 auto')
    parser.add_argument('--jobs', type=int, default=DEFAULT_JOBS,
                        help='并行 git log 的并发数（默认 16）')
    args = parser.parse_args()

    if args.jobs < 1:
        args.jobs = DEFAULT_JOBS

    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print(json.dumps({'error': f'日期格式错误: {args.date}，应为 YYYY-MM-DD'}, ensure_ascii=False))
        return

    if not os.path.isdir(args.root):
        print(json.dumps({'error': f'代码主目录不存在: {args.root}'}, ensure_ascii=False))
        return

    # 确定作者过滤策略
    author_filter = args.author
    if author_filter is None or author_filter == 'auto':
        author_filter = get_git_user_name()
    elif author_filter == 'all':
        author_filter = None

    repos = find_git_repos(args.root, args.max_depth)

    result = {
        'date': args.date,
        'root': args.root,
        'author_filter': author_filter,
        'repos_scanned': len(repos),
        'projects': [],
    }

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        all_commits = list(executor.map(
            functools.partial(collect_git_log, date_str=args.date, author=author_filter),
            repos,
        ))

    for repo, commits in zip(repos, all_commits):
        if commits:
            result['projects'].append({
                'path': repo,
                'name': os.path.basename(repo),
                'commits': commits,
            })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

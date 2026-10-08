#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bump_visitors.py —— 给个人网站 VisitorMap 访客统计"补次数"

数据源与 src/components/VisitorMap.astro 里完全一致。注意：该 KV 服务对
URL 长度有硬限制（解码后约 280 字符），单 key 存不下全部国家，因此数据
按国家代码首字母分 3 片存储，读写都走分片：

    GET  https://keyvalue.immanuel.co/api/KeyVal/GetValue/yg2u5sb4/site-visits-1
    GET  .../site-visits-2
    GET  .../site-visits-3
    POST .../UpdateValue/yg2u5sb4/site-visits-N/{value}   # N=1|2|3，只写目标片
存储格式：CC=count,CC=count,...（= 和 , 不需要 URL 编码）

用法示例：
    python tools/bump_visitors.py                     # CN +1
    python tools/bump_visitors.py --count 50          # CN +50
    python tools/bump_visitors.py --region US --count 20
    python tools/bump_visitors.py --region CN --region US --region JP --count 5
    python tools/bump_visitors.py --random 300        # 总共随机刷 300 次访问（按常见度加权，可重复）
    python tools/bump_visitors.py --random 2000 --batch-size 100 --interval 1.0
                                                      # 每批 100 次、批间停 1 秒，防屏蔽
    python tools/bump_visitors.py --dry-run           # 只读当前数据，不写入
防屏蔽机制：总次数按 --batch-size 拆批（默认 100），每批写完暂停
--interval 秒（默认 1 秒），单批内也只发 3 个分片请求，节奏远低于真实访客。
仅使用 Python 标准库，无需安装任何依赖。
"""

import argparse
import json
import random
import sys
import time
import urllib.request

APP_KEY = "yg2u5sb4"
STORE_BASE = "https://keyvalue.immanuel.co/api/KeyVal"

# 分片：按国家代码首字母区间划分，与 VisitorMap.astro 中的 SHARDS 保持一致
SHARDS = [
    ("site-visits-1", ("A", "F")),
    ("site-visits-2", ("G", "N")),
    ("site-visits-3", ("O", "Z")),
]

# 用于 --random 时挑选的常见国家和地区（ISO 3166-1 alpha-2）
COMMON_REGIONS = [
    "CN", "US", "JP", "KR", "SG", "HK", "TW", "IN", "GB", "DE",
    "FR", "CA", "AU", "NL", "RU", "BR", "MX", "MY", "TH",
    "VN", "ID", "PH", "AE", "SA", "TR", "PL", "SE", "CH", "IT",
    "ES", "NZ", "AR", "ZA", "EG", "NG", "UA", "CZ", "AT", "BE",
]


def shard_key_of(cc: str) -> str:
    """按国家代码首字母定位所在分片 key"""
    for key, (lo, hi) in SHARDS:
        if lo <= cc[0] <= hi:
            return key
    return SHARDS[-1][0]


def read_counts() -> dict:
    """读取所有分片并合并，返回 {国家代码: 次数}"""
    counts: dict = {}
    for key, _ in SHARDS:
        url = f"{STORE_BASE}/GetValue/{APP_KEY}/{key}"
        with urllib.request.urlopen(url, timeout=15) as r:
            body = r.read().decode("utf-8")
        # 服务返回带引号的 JSON 字符串（如 "CN=4,US=2"），剥掉外层引号
        try:
            text = json.loads(body)
        except json.JSONDecodeError:
            text = body.strip()
        for part in str(text).split(","):
            part = part.strip()
            if not part or "=" not in part:
                continue
            cc, _, n = part.partition("=")
            cc = cc.strip().upper()
            try:
                counts[cc] = int(n)
            except ValueError:
                continue
    return counts


def write_counts(counts: dict) -> None:
    """把完整计数按分片写回（每片 URL 都很短，避开服务端 URL 长度限制）"""
    by_shard = {key: [] for key, _ in SHARDS}
    for cc, n in counts.items():
        by_shard[shard_key_of(cc)].append(f"{cc}={n}")
    for key, items in by_shard.items():
        if not items:
            continue
        value = ",".join(items)
        # = 与 , 是 URL 路径段合法字符，无需编码（编码反而撑长 URL）
        url = f"{STORE_BASE}/UpdateValue/{APP_KEY}/{key}/{value}"
        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(url, method="POST")
                with urllib.request.urlopen(req, timeout=15) as r:
                    body = r.read().decode("utf-8")
                print(f"[写入] {key}: HTTP {r.status}（URL {len(url)} 字符），响应: {body[:120]}")
                break
            except Exception as e:
                if attempt == 3:
                    raise
                print(f"[重试] {key} 写入失败（{e}），2 秒后重试 {attempt + 1}/3…")
                time.sleep(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="给 VisitorMap 访客统计补访问次数"
    )
    parser.add_argument(
        "--count", type=int, default=1, help="每个目标国家增加多少次（默认 1）"
    )
    parser.add_argument(
        "--region", action="append", default=[],
        help="要增加的国家/地区代码（ISO alpha-2，可多次指定，默认 CN）",
    )
    parser.add_argument(
        "--random", type=int, metavar="N",
        help="总共随机刷 N 次访问（按常见度加权、允许重复），与 --region/--count 互斥",
    )
    parser.add_argument(
        "--batch-size", type=int, default=100,
        help="每批刷多少次后暂停（默认 100，防止高频请求被服务端屏蔽）",
    )
    parser.add_argument(
        "--interval", type=float, default=1.0,
        help="批次之间的暂停秒数（默认 1 秒）",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只读取并展示，不写入",
    )
    args = parser.parse_args()

    if args.batch_size <= 0 or args.interval < 0:
        print("--batch-size 必须为正整数，--interval 不能为负", file=sys.stderr)
        return 2

    before = read_counts()
    total_before = sum(before.values())
    print(f"[读取] 当前计数: {before}")
    print(f"[读取] 当前总访问: {total_before}，覆盖 {len(before)} 个国家和地区\n")

    if args.dry_run:
        print("[dry-run] 未做任何写入。")
        return 0

    # 生成增量列表（统一成 picks，方便按批消费）
    if args.random is not None:
        if args.random <= 0:
            print("--random 必须为正整数", file=sys.stderr)
            return 2
        if args.count != 1 or args.region:
            print("提示: --random 与 --region/--count 互斥，已忽略后两者")
        # 按常见度加权随机分配（CN 最常出现、依次递减，模拟真实分布）
        weights = [
            max(1, int(60 * (0.82 ** i))) for i in range(len(COMMON_REGIONS))
        ]
        picks = random.choices(COMMON_REGIONS, weights=weights, k=args.random)
        note = f"共 {args.random} 次随机访问"
    else:
        targets = [r.upper() for r in args.region] or ["CN"]
        for cc in targets:
            if not cc.isalpha() or len(cc) != 2:
                print(f"非法国家代码: {cc}（应为两位字母，如 CN/US/JP）", file=sys.stderr)
                return 2
        if args.count <= 0:
            print("--count 必须为正整数", file=sys.stderr)
            return 2
        picks = [cc for cc in targets for _ in range(args.count)]
        note = f"目标 {targets}，各 +{args.count} 次"

    total = len(picks)
    if total <= 0:
        print("没有需要刷的次数，退出", file=sys.stderr)
        return 2
    batches = (total + args.batch_size - 1) // args.batch_size
    if batches > 1:
        print(
            f"[批次] 共 {total} 次，分 {batches} 批，"
            f"每批 ≤{args.batch_size} 次，批间暂停 {args.interval} 秒\n"
        )

    after = dict(before)
    done = 0
    for bi in range(batches):
        chunk = picks[bi * args.batch_size : (bi + 1) * args.batch_size]
        dist = {cc: chunk.count(cc) for cc in set(chunk)}
        for cc, n in dist.items():
            after[cc] = after.get(cc, 0) + n
        done += len(chunk)
        print(f"[批次] 第 {bi + 1}/{batches} 批：+{len(chunk)} 次（累计 {done}/{total}）")
        write_counts(after)
        if bi < batches - 1:
            print(f"[等待] 暂停 {args.interval} 秒，避免请求过密…\n")
            time.sleep(args.interval)

    print(f"\n[结果] {note}")
    print(f"[结果] 变化: {total_before} -> {sum(after.values())} 次"
          f"（+{sum(after.values()) - total_before}），"
          f"{len(before)} -> {len(after)} 个国家和地区")

    # 读回验证
    verify = read_counts()
    if verify == after:
        print("[验证] 读回一致，写入成功 ✔")
    else:
        print(f"[验证] 读回不一致！实际: {verify}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

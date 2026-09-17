#!/usr/bin/env python3
"""
生成 src/data/world-map.json —— 访客地图用的点阵世界地图 + 国家中心点表。

为什么要构建期生成：
  Visitors 组件要画一张"哪里有人访问就亮一个点"的世界地图。运行时去拉 GeoJSON、
  再栅格化，会让首屏多一次网络请求和一段几百毫秒的计算；而这张图是不变的，
  所以直接预计算成一小段 base64 位图存进仓库（约 960 字符），组件里解码即可。

用法：
    pip install nothing   # 纯标准库
    python tools/gen-world-map.py

需要先准备两个输入文件（放在仓库根目录，生成完可删）：

  1. world110.json —— 国家边界 TopoJSON
     https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json
     （来源：Natural Earth 1:110m，via world-atlas，ISC 许可）

  2. isocodes.json —— ISO 3166 代码对照表，用来把 TopoJSON 里的数字 id 转成
     alpha-2（因为 ip 定位服务返回的是 alpha-2，比如 CN / US / JP）
     https://cdn.jsdelivr.net/npm/i18n-iso-countries@7.11.0/codes.json

输出结构：
    {
      "ncol": 120, "nrow": 48,           # 点阵网格
      "lon0": -180, "lat0": 84, "step": 3,  # 左上角与格距（度）
      "mask": "<base64>",                # 逐行 1bit，1 = 陆地
      "centroids": { "CN": [103.87, 36.61], ... }  # 国家中心点
    }

坐标系约定（组件里也按这个换算）：
    viewBox = 0 0 360 144，x = lon + 180，y = 84 - lat，1 单位 = 1 度。

裁剪范围 lat ∈ [-60, 84]：去掉南极洲，并把图幅收成常见的 2.5:1 世界地图比例。
"""
import base64
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPO_PATH = os.path.join(ROOT, "world110.json")
ISO_PATH = os.path.join(ROOT, "isocodes.json")
OUT_PATH = os.path.join(ROOT, "src", "data", "world-map.json")

# ---- 网格参数 ----
LON0, LAT0, STEP = -180.0, 84.0, 3.0
NCOL, NROW = 120, 48
LAT1 = LAT0 - NROW * STEP  # -60.0

# 有些小国/地区在 110m 精度下太小或干脆没有，手工补中心点（经度, 纬度）
SUPPLEMENT = {
    "SG": [103.82, 1.35], "HK": [114.17, 22.32], "MO": [113.55, 22.20],
    "MT": [14.51, 35.90], "MC": [7.42, 43.73], "BH": [50.55, 26.07],
    "MV": [73.51, 4.18], "MU": [57.55, -20.28], "SC": [55.49, -4.62],
    "LI": [9.52, 47.14], "SM": [12.46, 43.94], "AD": [1.52, 42.51],
    "VA": [12.45, 41.90], "LC": [-60.98, 13.91], "BB": [-59.54, 13.19],
    "GD": [-61.68, 12.12], "VC": [-61.20, 13.25], "AG": [-61.80, 17.08],
    "KN": [-62.73, 17.30], "DM": [-61.37, 15.42], "TO": [-175.20, -21.18],
    "WS": [-172.10, -13.76], "KI": [172.98, 1.45], "PW": [134.58, 7.51],
    "MH": [171.18, 7.13], "FM": [158.22, 6.89], "NR": [166.93, -0.53],
    "TV": [179.20, -8.52], "LU": [6.13, 49.82], "CY": [33.43, 35.13],
    "BN": [114.73, 4.54], "TL": [125.73, -8.84], "FJ": [178.07, -17.71],
    "SB": [160.16, -9.65], "VU": [166.96, -15.38], "PG": [143.91, -6.49],
    "JE": [-2.13, 49.21], "GG": [-2.58, 49.47], "IM": [-4.55, 54.24],
    "GI": [-5.35, 36.14], "FO": [-6.91, 62.00], "GL": [-41.47, 74.12],
    "NC": [165.62, -21.27], "PF": [-149.41, -17.68], "GU": [144.79, 13.44],
    "PR": [-66.43, 18.22], "BM": [-64.75, 32.31], "KY": [-81.25, 19.31],
    "AW": [-69.97, 12.52], "CW": [-68.97, 12.20], "MQ": [-61.02, 14.64],
    "GP": [-61.55, 16.25], "RE": [55.54, -21.11], "YT": [45.17, -12.83],
    "AX": [19.95, 60.18], "SJ": [16.00, 78.00],
}


def norm_lon(x):
    while x > 180:
        x -= 360
    while x < -180:
        x += 360
    return x


def lon2col(lon):
    return (lon - LON0) / STEP


def lat2row(lat):
    return (LAT0 - lat) / STEP


def point_in_ring(x, y, ring):
    inside, n = False, len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def unwrap(ring):
    """让经度连续，避免跨 180 度经线的环被误当成横跨全球的巨型多边形。"""
    out = [ring[0]]
    px = ring[0][0]
    for x, y in ring[1:]:
        while x - px > 180:
            x -= 360
        while x - px < -180:
            x += 360
        out.append((x, y))
        px = x
    return out


def ring_area_centroid(ring):
    a = cx = cy = 0.0
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if a == 0:
        return None
    a *= 0.5
    return (cx / (6 * a), cy / (6 * a), abs(a))


def main():
    for path in (TOPO_PATH, ISO_PATH):
        if not os.path.exists(path):
            sys.exit(f"缺少输入文件：{path}\n详见本文件顶部说明。")

    topo = json.load(open(TOPO_PATH, encoding="utf-8"))
    iso = json.load(open(ISO_PATH, encoding="utf-8"))
    num2a2 = {row[2]: row[0] for row in iso}

    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]

    def decode_arc(arc):
        pts, x, y = [], 0, 0
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        return pts

    arcs = [decode_arc(a) for a in topo["arcs"]]

    def ring_coords(arc_idxs):
        out = []
        for i in arc_idxs:
            seg = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(seg[1:] if out else seg)
        return out

    def geom_polygons(g):
        if g["type"] == "Polygon":
            return [ring_coords(r) for r in g["arcs"]]
        return [ring_coords(poly[0]) for poly in g["arcs"]]

    land = [[0] * NCOL for _ in range(NROW)]

    def mark_ring(ring):
        if len(ring) < 4:
            return
        pts = unwrap(ring)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, x1 = min(xs), max(xs)
        if x1 - x0 > 180 or x0 < -180 or x1 > 180:
            c0, c1 = 0, NCOL - 1  # 跨经线的环必须全列扫描
        else:
            c0 = max(0, int(math.floor(lon2col(x0))))
            c1 = min(NCOL - 1, int(math.ceil(lon2col(x1))))
        r0 = max(0, int(math.floor(lat2row(max(ys)))))
        r1 = min(NROW - 1, int(math.ceil(lat2row(min(ys)))))
        for r in range(r0, r1 + 1):
            lat = LAT0 - (r + 0.5) * STEP
            for c in range(c0, c1 + 1):
                if land[r][c]:
                    continue
                lon = LON0 + (c + 0.5) * STEP
                for k in (-1, 0, 1):
                    if point_in_ring(lon + 360 * k, lat, pts):
                        land[r][c] = 1
                        break

    centroids = {}
    stats = {"area": 0, "unwrap": 0, "bbox": 0, "supplied": 0, "skipped": 0}

    for g in topo["objects"]["countries"]["geometries"]:
        code = num2a2.get(str(g.get("id", "")))
        polys = geom_polygons(g)
        if not polys:
            continue
        for ring in polys:
            mark_ring(ring)
        if not code:
            continue

        def inside(lon, lat):
            return any(point_in_ring(lon, lat, r) for r in polys)

        def area_c(rings):
            best = None
            for ring in rings:
                res = ring_area_centroid(ring)
                if res and (best is None or res[2] > best[2]):
                    best = res
            return best

        unwrapped = [unwrap(r) for r in polys]
        big = max(polys, key=lambda r: (ring_area_centroid(r) or (0, 0, 0))[2])
        big_u = unwrap(big)

        def bbox_c(ring):
            bx = [p[0] for p in ring]
            by = [p[1] for p in ring]
            return ((min(bx) + max(bx)) / 2, (min(by) + max(by)) / 2)

        candidates = []
        c1 = area_c(polys)
        if c1:
            candidates.append(("area", norm_lon(c1[0]), c1[1]))
        c2 = area_c(unwrapped)
        if c2:
            candidates.append(("unwrap", norm_lon(c2[0]), c2[1]))
        candidates.append(("bbox", norm_lon(bbox_c(big)[0]), bbox_c(big)[1]))
        candidates.append(("bbox", norm_lon(bbox_c(big_u)[0]), bbox_c(big_u)[1]))

        picked = next((c for c in candidates if inside(c[1], c[2])), None)
        if not picked:
            stats["skipped"] += 1
            continue

        label, lon, lat = picked
        stats[label] += 1
        if lat < LAT1 or lat > LAT0:
            continue  # 图幅外（如南极洲）
        centroids[code] = [round(lon, 2), round(lat, 2)]

    for code, pt in SUPPLEMENT.items():
        if code not in centroids:
            centroids[code] = pt
            stats["supplied"] += 1

    bits = [b for r in range(NROW) for b in land[r]]
    packed = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        chunk += [0] * (8 - len(chunk))
        v = 0
        for bit in chunk:
            v = (v << 1) | bit
        packed.append(v)
    mask = base64.b64encode(bytes(packed)).decode()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    json.dump(
        {
            "ncol": NCOL,
            "nrow": NROW,
            "lon0": LON0,
            "lat0": LAT0,
            "step": STEP,
            "mask": mask,
            "centroids": centroids,
        },
        open(OUT_PATH, "w", encoding="utf-8"),
        ensure_ascii=False,
    )

    print(f"网格        {NCOL} x {NROW}")
    print(f"陆地点      {sum(sum(r) for r in land)}")
    print(f"国家/地区   {len(centroids)}")
    print(f"掩码长度    {len(mask)} 字符 (base64)")
    print(f"中心点来源  质心 {stats['area']} / 展开质心 {stats['unwrap']} / "
          f"包围盒 {stats['bbox']} / 补点 {stats['supplied']} / 丢弃 {stats['skipped']}")
    print(f"输出        {OUT_PATH}")


if __name__ == "__main__":
    main()

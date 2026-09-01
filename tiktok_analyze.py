import json
import sys
from collections import defaultdict

FILE = sys.argv[1] if len(sys.argv) > 1 else "posts_sensulujuz40.json"
HASHTAG = sys.argv[2] if len(sys.argv) > 2 else "sensulujuz40"
MIN_VIEWS = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
TOP_N = 10

with open(FILE, encoding="utf-8") as f:
    posts = json.load(f)

def has_hashtag(p, tag):
    tag = tag.lower()
    for ch in (p.get("challenges") or []):
        if (ch.get("title") or "").lower() == tag:
            return True
    if f"#{tag}" in (p.get("desc") or "").lower():
        return True
    return False

def views_of(p):
    return int((p.get("stats") or {}).get("playCount", 0) or 0)

before = len(posts)
posts = [p for p in posts if has_hashtag(p, HASHTAG)]
print(f"Всего постов в файле: {before}")
print(f"Из них реально содержат #{HASHTAG}: {len(posts)} (отфильтровано {before - len(posts)} чужих)\n")

total_views = 0
users = defaultdict(lambda: {"views": 0, "likes": 0, "posts": 0, "nickname": ""})

for p in posts:
    stats = p.get("stats", {}) or {}
    author = p.get("author", {}) or {}
    uid = author.get("uniqueId", "unknown")
    views = views_of(p)
    likes = int(stats.get("diggCount", 0) or 0)
    total_views += views
    users[uid]["views"] += views
    users[uid]["likes"] += likes
    users[uid]["posts"] += 1
    users[uid]["nickname"] = author.get("nickname", "")

print(f"Суммарные просмотры постов с #{HASHTAG}: {total_views:,}\n")

ranking = sorted(users.items(), key=lambda x: x[1]["views"], reverse=True)

print("=" * 80)
print(f"ТОП-3 ПОЛЬЗОВАТЕЛЯ ПО ПРОСМОТРАМ (#{HASHTAG})")
print("=" * 80)
for i, (uid, d) in enumerate(ranking[:3], 1):
    print(f"{i}. @{uid} ({d['nickname']})")
    print(f"   Просмотры: {d['views']:,} | Лайки: {d['likes']:,} | Постов: {d['posts']}")
    print(f"   Профиль: https://www.tiktok.com/@{uid}\n")

print("-" * 80)
print(f"{'Место':<6}{'Пользователь':<28}{'Просмотры':>14}{'Лайки':>12}{'Постов':>8}")
print("-" * 80)
for i, (uid, d) in enumerate(ranking[:TOP_N], 1):
    print(f"{i:<6}@{uid:<27}{d['views']:>14,}{d['likes']:>12,}{d['posts']:>8}")

print()
print("=" * 80)
print(f"ТОП-3 САМЫХ ПРОСМАТРИВАЕМЫХ ПОСТА (#{HASHTAG})")
print("=" * 80)
top_posts = sorted(posts, key=views_of, reverse=True)
for i, p in enumerate(top_posts[:3], 1):
    author = p.get("author", {}) or {}
    uid = author.get("uniqueId", "unknown")
    print(f"{i}. @{uid} — {views_of(p):,} просмотров")
    print(f"   {p.get('desc', '')[:70]}")
    print(f"   https://www.tiktok.com/@{uid}/video/{p.get('id')}\n")

# ===== ВСЕ ВИДЕО С ПОРОГОМ ПРОСМОТРОВ =====
hits = [p for p in top_posts if views_of(p) >= MIN_VIEWS]

print("=" * 80)
print(f"ВСЕ ВИДЕО С #{HASHTAG} И {MIN_VIEWS:,}+ ПРОСМОТРОВ — найдено: {len(hits)}")
print("=" * 80)
print(f"{'№':<4}{'Пользователь':<26}{'Просмотры':>12}{'Лайки':>10}  Ссылка")
print("-" * 80)
for i, p in enumerate(hits, 1):
    stats = p.get("stats", {}) or {}
    author = p.get("author", {}) or {}
    uid = author.get("uniqueId", "unknown")
    likes = int(stats.get("diggCount", 0) or 0)
    link = f"https://www.tiktok.com/@{uid}/video/{p.get('id')}"
    print(f"{i:<4}@{uid:<25}{views_of(p):>12,}{likes:>10,}  {link}")

# Сохраняем список в CSV — удобно открыть в Excel/Numbers
if hits:
    import csv
    csv_name = f"videos_{HASHTAG}_{MIN_VIEWS}plus.csv"
    with open(csv_name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["user", "nickname", "views", "likes", "comments", "shares", "description", "link"])
        for p in hits:
            stats = p.get("stats", {}) or {}
            author = p.get("author", {}) or {}
            uid = author.get("uniqueId", "unknown")
            w.writerow([
                uid,
                author.get("nickname", ""),
                views_of(p),
                int(stats.get("diggCount", 0) or 0),
                int(stats.get("commentCount", 0) or 0),
                int(stats.get("shareCount", 0) or 0),
                (p.get("desc") or "").replace("\n", " "),
                f"https://www.tiktok.com/@{uid}/video/{p.get('id')}",
            ])
    print(f"\nСписок также сохранён в {csv_name} (открывается в Excel)")

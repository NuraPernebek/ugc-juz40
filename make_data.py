# -*- coding: utf-8 -*-
"""
make_data.py — собирает все posts_*.json (из tiktok_scrape.py)
в один файл data.json для сайта аналитики JUZ40.

Запуск:
    python make_data.py                  # возьмёт все posts_*.json в папке
    python make_data.py posts_a.json posts_b.json

Дальше:
    Загрузите data.json в свой GitHub-репозиторий (замените старый файл).
    Сайт подхватит данные автоматически.
"""
import json
import sys
import glob
from datetime import datetime, timezone
from collections import defaultdict

# ==== Конкурсные хэштеги (как в tiktok_report.py) ====
CONTESTS = [
    "juz40jurekte",
    "juz40online",
    "juz40fest26",
    "juz40fest",
    "juz40пен140",
    "juz40жүрегімде",
]

TOP_VIDEOS_LIMIT = 50   # сколько видео показывать на сайте
TOP_USERS_LIMIT = 50    # сколько участников показывать на сайте

files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob("posts_*.json"))
if not files:
    print("posts_*.json не найдены. Сначала запустите tiktok_scrape.py")
    raise SystemExit(1)

posts = {}
for fn in files:
    with open(fn, encoding="utf-8") as f:
        for p in json.load(f):
            posts[p["id"]] = p  # дубликаты убираются
posts = list(posts.values())


def stat(p, key):
    return int((p.get("stats") or {}).get(key, 0) or 0)


def tags_of(p):
    tags = {(ch.get("title") or "").lower() for ch in (p.get("challenges") or [])}
    desc = (p.get("desc") or "").lower()
    for t in CONTESTS:
        if f"#{t.lower()}" in desc:
            tags.add(t.lower())
    return tags


contest_set = {t.lower() for t in CONTESTS}
posts = [p for p in posts if tags_of(p) & contest_set]

# ---- пользователи ----
users = defaultdict(lambda: {"views": 0, "likes": 0, "comments": 0, "shares": 0,
                             "posts": 0, "nickname": ""})
for p in posts:
    a = p.get("author") or {}
    uid = a.get("uniqueId", "unknown")
    u = users[uid]
    u["views"] += stat(p, "playCount")
    u["likes"] += stat(p, "diggCount")
    u["comments"] += stat(p, "commentCount")
    u["shares"] += stat(p, "shareCount")
    u["posts"] += 1
    u["nickname"] = a.get("nickname", "")

top_users = sorted(
    ({"user": uid, **d} for uid, d in users.items()),
    key=lambda x: x["views"], reverse=True
)[:TOP_USERS_LIMIT]

# ---- видео ----
videos = sorted(posts, key=lambda p: stat(p, "playCount"), reverse=True)[:TOP_VIDEOS_LIMIT]
top_videos = []
for p in videos:
    a = p.get("author") or {}
    uid = a.get("uniqueId", "unknown")
    top_videos.append({
        "user": uid,
        "nickname": a.get("nickname", ""),
        "desc": (p.get("desc") or "").replace("\n", " ")[:120],
        "views": stat(p, "playCount"),
        "likes": stat(p, "diggCount"),
        "comments": stat(p, "commentCount"),
        "link": f"https://www.tiktok.com/@{uid}/video/{p.get('id')}",
    })

# ---- по хэштегам ----
by_hashtag = []
for tag in CONTESTS:
    tl = tag.lower()
    group = [p for p in posts if tl in tags_of(p)]
    if not group:
        continue
    by_hashtag.append({
        "tag": tag,
        "videos": len(group),
        "views": sum(stat(p, "playCount") for p in group),
        "likes": sum(stat(p, "diggCount") for p in group),
    })

data = {
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "hashtags": CONTESTS,
    "totals": {
        "videos": len(posts),
        "views": sum(stat(p, "playCount") for p in posts),
        "likes": sum(stat(p, "diggCount") for p in posts),
        "comments": sum(stat(p, "commentCount") for p in posts),
        "users": len(users),
    },
    "byHashtag": by_hashtag,
    "topUsers": top_users,
    "topVideos": top_videos,
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

t = data["totals"]
print(f"Готово: data.json")
print(f"  Видео: {t['videos']:,} | Просмотры: {t['views']:,} | "
      f"Лайки: {t['likes']:,} | Участников: {t['users']:,}")
print("Теперь загрузите data.json в GitHub-репозиторий (замените старый).")

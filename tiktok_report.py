import json
import sys
import glob
from collections import defaultdict

# ==== ТІЗІМДІ ӨЗІҢІЗ РЕТТЕҢІЗ: конкурс хэштегтері ====
CONTESTS = [
    "sensulujuz40",
    "juz40online",
    "juz40festbts",
    "juz40fest",
    "juz40пен140",
    "juz40жүрегімде",
]

# Файлы: перечислить аргументами или возьмёт все posts_*.json
files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob("posts_*.json"))
if not files:
    print("posts_*.json файлдары табылмады. Алдымен скрейперді іске қосыңыз.")
    raise SystemExit(1)

posts = {}
for fn in files:
    with open(fn, encoding="utf-8") as f:
        for p in json.load(f):
            posts[p["id"]] = p          # дубликаттар автоматты түрде алынады
posts = list(posts.values())

def views_of(p):
    return int((p.get("stats") or {}).get("playCount", 0) or 0)

def likes_of(p):
    return int((p.get("stats") or {}).get("diggCount", 0) or 0)

def tags_of(p):
    tags = {(ch.get("title") or "").lower() for ch in (p.get("challenges") or [])}
    desc = (p.get("desc") or "").lower()
    for t in CONTESTS:
        if f"#{t.lower()}" in desc:
            tags.add(t.lower())
    return tags

# Тек конкурс хэштегі бар посттар
contest_set = {t.lower() for t in CONTESTS}
posts = [p for p in posts if tags_of(p) & contest_set]

total_videos = len(posts)
total_views = sum(views_of(p) for p in posts)
avg_views = total_views / total_videos if total_videos else 0

lines = []
def out(s=""):
    print(s)
    lines.append(s)

out("=" * 70)
out("JUZ40 — ЖАЛПЫ ЕСЕП")
out(f"Деректер көзі: {', '.join(files)}")
out("=" * 70)
out(f"Қанша видео жарияланды:      {total_videos:,}")
out(f"Жалпы қанша просмотр болды:  {total_views:,}")
out(f"Орташа просмотр саны:        {avg_views:,.0f}")
out()
out("=" * 70)
out("ӘР КОНКУРС БОЙЫНША ЖЕКЕ СТАТИСТИКА")
out("=" * 70)
out(f"{'Конкурс':<22}{'Видео':>8}{'Просмотр':>15}{'Орташа':>12}{'Лайк':>12}")
out("-" * 70)

for tag in CONTESTS:
    tl = tag.lower()
    group = [p for p in posts if tl in tags_of(p)]
    if not group:
        out(f"#{tag:<21}{'—':>8}{'—':>15}{'—':>12}{'—':>12}")
        continue
    v = sum(views_of(p) for p in group)
    l = sum(likes_of(p) for p in group)
    out(f"#{tag:<21}{len(group):>8,}{v:>15,}{v/len(group):>12,.0f}{l:>12,}")

out("-" * 70)
out("Ескерту: бір видеода бірнеше конкурс хэштегі болуы мүмкін,")
out("сондықтан конкурстар қосындысы жалпы саннан артық болуы мүмкін.")
out()

# Әр конкурстың ең үздік видеосы
out("=" * 70)
out("ӘР КОНКУРСТЫҢ ЕҢ КӨП ҚАРАЛҒАН ВИДЕОСЫ")
out("=" * 70)
for tag in CONTESTS:
    tl = tag.lower()
    group = [p for p in posts if tl in tags_of(p)]
    if not group:
        continue
    top = max(group, key=views_of)
    uid = (top.get("author") or {}).get("uniqueId", "unknown")
    out(f"#{tag}")
    out(f"   @{uid} — {views_of(top):,} просмотр")
    out(f"   https://www.tiktok.com/@{uid}/video/{top.get('id')}")
    out()

with open("report_juz40.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Есеп report_juz40.txt файлына сақталды")

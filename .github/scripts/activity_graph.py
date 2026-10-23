"""Write one contribution graph (SVG) that adds up the GitHub calendars of several users.

GitHub has no contribution graph for an organization, so the org profile shows its members' calendars summed
per day. With --org, only contributions to that organization's repos count, and the users default to its
members. Stdlib only.

Usage: GITHUB_TOKEN=... python activity_graph.py OUT.svg [--org ORG] [LOGIN...]
"""

import datetime as dt
import json
import os
import sys
import urllib.request

QUERY = """query($login: String!, $org: ID) { user(login: $login) {
  contributionsCollection(organizationID: $org) { contributionCalendar {
  weeks { contributionDays { date contributionCount } } } } } }"""
CELL, GAP, LEFT, TOP = 10, 3, 28, 20
LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DARK = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def api(token: str, path: str, query: dict | None = None):
    url = "https://api.github.com/" + path
    body = json.dumps(query).encode() if query else None
    req = urllib.request.Request(url, data=body, headers={"Authorization": f"bearer {token}"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if isinstance(data, dict) and data.get("errors"):
        raise SystemExit(f"{path}: {data['errors'][0]['message']}")
    return data


def calendar(login: str, token: str, org_id: str | None) -> dict[str, int]:
    data = api(token, "graphql", {"query": QUERY, "variables": {"login": login, "org": org_id}})
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}


def level(count: int, top: int) -> int:
    if count == 0 or top == 0:
        return 0
    return min(4, 1 + (4 * (count - 1)) // top)


def svg(days: dict[str, int], logins: list[str], org: str | None) -> str:
    dates = sorted(days)
    first = dt.date.fromisoformat(dates[0])
    first -= dt.timedelta(days=(first.weekday() + 1) % 7)  # weeks start on Sunday, as on GitHub
    top = max(days.values())
    cells, months, last_month = [], [], None
    for iso in dates:
        day = dt.date.fromisoformat(iso)
        week, weekday = (day - first).days // 7, (day.weekday() + 1) % 7
        x, y = LEFT + week * (CELL + GAP), TOP + weekday * (CELL + GAP)
        cells.append(
            f'<rect class="l{level(days[iso], top)}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2">'
            f"<title>{iso}: {days[iso]}</title></rect>"
        )
        if weekday == 0 and day.month != last_month:
            months.append(f'<text x="{x}" y="{TOP - 7}">{day.strftime("%b")}</text>')
            last_month = day.month
    width = LEFT + ((dt.date.fromisoformat(dates[-1]) - first).days // 7 + 1) * (CELL + GAP)
    height = TOP + 7 * (CELL + GAP) + 22
    total = sum(days.values())
    where = f" to {org} repos" if org else ""
    caption = f"{total} contributions{where} in the last year ({' + '.join(logins)})"
    styles = "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(LIGHT))
    dark = "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(DARK))
    labels = "".join(
        f'<text x="0" y="{TOP + d * (CELL + GAP) + 9}">{name}</text>' for d, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f"<style>text{{font:10px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#57606a}}{styles}"
        f"@media (prefers-color-scheme: dark){{text{{fill:#8b949e}}{dark}}}</style>"
        f"{''.join(months)}{labels}{''.join(cells)}"
        f'<text x="{LEFT}" y="{height - 6}">{caption}</text></svg>\n'
    )


def main() -> None:
    out, args = sys.argv[1], sys.argv[2:]
    token = os.environ["GITHUB_TOKEN"]
    org = org_id = None
    if args[:1] == ["--org"]:
        org, args = args[1], args[2:]
        org_id = api(token, f"orgs/{org}")["node_id"]
        args = args or sorted(m["login"] for m in api(token, f"orgs/{org}/members?per_page=100"))
    if not args:
        raise SystemExit("No users: pass logins (org members are private unless made public).")
    days: dict[str, int] = {}
    for login in args:
        for iso, count in calendar(login, token, org_id).items():
            days[iso] = days.get(iso, 0) + count
    with open(out, "w") as f:
        f.write(svg(days, args, org))


if __name__ == "__main__":
    main()

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
CELL, GAP = 10, 3
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


def svg(days: dict[str, int]) -> str:
    """The grid only: no labels, no caption."""
    dates = sorted(days)
    first = dt.date.fromisoformat(dates[0])
    first -= dt.timedelta(days=(first.weekday() + 1) % 7)  # weeks start on Sunday, as on GitHub
    top = max(days.values())
    cells = []
    for iso in dates:
        day = dt.date.fromisoformat(iso)
        week, weekday = (day - first).days // 7, (day.weekday() + 1) % 7
        cells.append(
            f'<rect class="l{level(days[iso], top)}" x="{week * (CELL + GAP)}" y="{weekday * (CELL + GAP)}" '
            f'width="{CELL}" height="{CELL}" rx="2"><title>{iso}: {days[iso]}</title></rect>'
        )
    width = ((dt.date.fromisoformat(dates[-1]) - first).days // 7 + 1) * (CELL + GAP) - GAP
    height = 7 * (CELL + GAP) - GAP
    light = "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(LIGHT))
    dark = "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(DARK))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f"<style>{light}@media (prefers-color-scheme: dark){{{dark}}}</style>{''.join(cells)}</svg>\n"
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
        f.write(svg(days))


if __name__ == "__main__":
    main()

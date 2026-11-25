#!/usr/bin/env python3
"""Build the agent workforce status page from agents/roster.json.

    python3 -I agents/roster_status.py --state agents/logs/roster-state.json --out /tmp/roster/index.html

roster.json says who the agents are. The state file says what the Roster Keeper
saw on its last check (see ROSTER-KEEPER-PROMPT.md for its shape):

    {"checkedAt": "2026-11-25T07:05:00Z",
     "agents": {"<id>": {"lastRun": "<iso>", "result": "ok|did_work|failed|needs_alan|skipped",
                         "note": "<one line>", "source": "task|workflow|heartbeat|git"}},
     "endcard": {"checked": 120, "missing": 0},
     "needsAlan": ["<one plain line>", ...]}

Health per agent: failed and needs_alan come from the state; "late" means the
last run is older than 1.5 x cadenceHours; building and scheduled rows come from
the roster. Nothing here calls the network. Prints a one-line summary to stdout.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

MT = ZoneInfo("America/Denver")
HERE = Path(__file__).resolve().parent

HEALTH_LABEL = {
    "ok": "On schedule",
    "late": "Late",
    "failed": "Failed",
    "needs_alan": "Needs Alan",
    "building": "Being built",
    "scheduled": "Scheduled",
    "nosignal": "No signal yet",
}
HEALTH_ORDER = ["failed", "needs_alan", "late", "nosignal", "scheduled", "building", "ok"]


def parse_iso(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def health_of(agent, seen, now):
    status = agent.get("status")
    if status == "building":
        return "building"
    if status == "scheduled":
        return "scheduled"
    result = (seen or {}).get("result")
    if result == "failed":
        return "failed"
    if result == "needs_alan":
        return "needs_alan"
    last = parse_iso((seen or {}).get("lastRun"))
    cadence = agent.get("cadenceHours")
    if last is None:
        # event-driven or outside tools with no clock: trust a recorded ok
        if not cadence and result in ("ok", "did_work"):
            return "ok"
        return "nosignal"
    if cadence and (now - last).total_seconds() > cadence * 1.5 * 3600:
        return "late"
    return "ok"


def when_text(value, now):
    t = parse_iso(value)
    if t is None:
        return "No run seen"
    local = t.astimezone(MT)
    hours = (now - t).total_seconds() / 3600
    if hours < 1:
        ago = f"{max(1, round(hours * 60))} min ago"
    elif hours < 48:
        ago = f"{round(hours)} h ago"
    else:
        ago = f"{round(hours / 24)} days ago"
    clock = local.strftime("%-I:%M %p").lower().replace(" ", " ")
    return f"{local.strftime('%a %b %-d')}, {clock} ({ago})"


def last_text(agent, seen, health, now):
    if agent.get("status") == "building":
        return "Not running yet"
    if not seen.get("lastRun"):
        if health == "ok":
            return "Runs on events"
        if agent.get("status") == "scheduled":
            return "Not due yet"
    return when_text(seen.get("lastRun"), now)


TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*(am|pm)", re.I)


def daily_times(agent):
    """Minutes after midnight (Mountain) for agents that run every day."""
    if agent.get("times"):
        out = []
        for t in agent["times"]:
            h, m = t.split(":")
            out.append(int(h) * 60 + int(m))
        return out
    sched = agent.get("schedule") or ""
    if not sched.lower().startswith("daily"):
        return []
    out = []
    for h, m, ap in TIME_RE.findall(sched):
        h = int(h) % 12 + (12 if ap.lower() == "pm" else 0)
        out.append(h * 60 + int(m))
    return out


DAYS = [("Mon", ("monday", "mon ")), ("Tue", ("tue",)), ("Wed", ("wed",)), ("Thu", ("thu",)),
        ("Fri", ("fri",)), ("Sat", ("sat",)), ("Sun", ("sunday", "sun "))]


def weekly_days(agent):
    sched = (agent.get("schedule") or "").lower() + " "
    if sched.startswith("daily") or "a day" in sched or "every" in sched or "once" in sched:
        return []
    days = [d for d, keys in DAYS if any(k in sched for k in keys)]
    return days


def build(roster, state, now):
    seen_all = state.get("agents", {})
    agents = roster["agents"]
    rows = []
    for a in agents:
        seen = seen_all.get(a["id"], {})
        rows.append((a, seen, health_of(a, seen, now)))

    counts = {k: 0 for k in HEALTH_LABEL}
    for _, _, h in rows:
        counts[h] += 1
    working = [r for r in rows if r[0].get("status") not in ("building", "scheduled")]
    on_time = sum(1 for r in working if r[2] == "ok")
    trouble = [r for r in rows if r[2] in ("failed", "needs_alan", "late")]
    checked = parse_iso(state.get("checkedAt")) or now
    checked_local = checked.astimezone(MT)

    if trouble:
        headline = f"{on_time} of {len(working)} working agents ran on schedule. {len(trouble)} need a look."
    else:
        headline = f"All {on_time} working agents that report in ran on schedule." if not counts["nosignal"] else \
            f"{on_time} of {len(working)} working agents ran on schedule; none failed."

    teams = {t["id"]: t["name"] for t in roster.get("teams", [])}

    # ---- day band (24 h, Mountain) ----
    now_local = now.astimezone(MT)
    now_min = now_local.hour * 60 + now_local.minute
    lanes = []
    for tid, tname in teams.items():
        ticks = []
        for a, seen, h in rows:
            if a["team"] != tid:
                continue
            for m in daily_times(a):
                ticks.append((m, a, h))
        if ticks:
            lanes.append((tname, sorted(ticks, key=lambda x: x[0])))
    W, lane_h, top, left = 1100, 34, 26, 178
    H = top + lane_h * len(lanes) + 20
    svg = [f'<svg class="band" viewBox="0 0 {W} {H}" role="img" aria-label="When each daily agent runs, Mountain time">']
    for hr in range(0, 25, 3):
        x = left + (W - left) * hr / 24
        label = "12 am" if hr in (0, 24) else ("12 pm" if hr == 12 else (f"{hr} am" if hr < 12 else f"{hr - 12} pm"))
        svg.append(f'<line x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{H - 14}" class="grid"/>')
        anchor = "start" if hr == 0 else ("end" if hr == 24 else "middle")
        svg.append(f'<text x="{x:.1f}" y="{top - 12}" text-anchor="{anchor}" class="axis">{label}</text>')
    for i, (tname, ticks) in enumerate(lanes):
        y = top + i * lane_h
        svg.append(f'<rect x="{left - 6}" y="{y + 4}" width="{W - left + 6}" height="{lane_h - 8}" rx="6" class="lane"/>')
        svg.append(f'<text x="0" y="{y + lane_h / 2 + 4}" class="lanelabel">{esc(tname)}</text>')
        for m, a, h in ticks:
            x = left + (W - left) * m / 1440
            svg.append(f'<g class="tick h-{h}"><title>{esc(a["name"])}: {esc(a["schedule"])}</title>'
                       f'<rect x="{x - 3:.1f}" y="{y + 8}" width="6" height="{lane_h - 16}" rx="2"/></g>')
    nx = left + (W - left) * now_min / 1440
    svg.append(f'<line x1="{nx:.1f}" y1="{top - 4}" x2="{nx:.1f}" y2="{H - 14}" class="now"/>')
    now_anchor = "end" if nx > W - 20 else ("start" if nx < left + 20 else "middle")
    svg.append(f'<text x="{nx:.1f}" y="{H - 2}" text-anchor="{now_anchor}" class="nowlabel">now</text>')
    svg.append("</svg>")

    # ---- week strip ----
    week = {d: [] for d, _ in DAYS}
    for a, seen, h in rows:
        for d in weekly_days(a):
            week[d].append((a, h))
    week_html = ['<div class="week">']
    for d, _ in DAYS:
        week_html.append(f'<div class="day"><div class="dayname">{d}</div>')
        for a, h in week[d]:
            week_html.append(f'<div class="chip h-{h}"><span class="lamp"></span>{esc(a["name"])}</div>')
        if not week[d]:
            week_html.append('<div class="chip empty">Daily crews only</div>')
        week_html.append("</div>")
    week_html.append("</div>")

    # ---- needs a look ----
    attention = list(state.get("needsAlan") or [])
    look = []
    for a, seen, h in sorted(trouble, key=lambda r: HEALTH_ORDER.index(r[2])):
        note = seen.get("note") or ""
        look.append(f'<li><span class="pill h-{h}">{HEALTH_LABEL[h]}</span> <b>{esc(a["name"])}</b>'
                    f'{(": " + esc(note)) if note else ""} <span class="muted">Owner: {esc(a.get("owner"))}</span></li>')

    # ---- team tables ----
    sections = []
    for tid, tname in teams.items():
        team_rows = [r for r in rows if r[0]["team"] == tid]
        if not team_rows:
            continue
        trs = []
        for a, seen, h in team_rows:
            note = seen.get("note") or ""
            runner = a.get("runner", {})
            kind = {"task": "Scheduled task", "workflow": "GitHub workflow", "app": "App code",
                    "external": "Paid tool"}.get(runner.get("kind"), "")
            trs.append(
                "<tr>"
                f'<td class="agent"><div class="who"><span class="lamp h-{h}"></span><div><b>{esc(a["name"])}</b>'
                f'<div class="does">{esc(a["does"])}</div></div></div></td>'
                f'<td>{esc(a.get("schedule"))}<div class="muted">{esc(kind)}</div></td>'
                f'<td>{esc(last_text(a, seen, h, now))}'
                f'{("<div class=muted>" + esc(note) + "</div>") if note else ""}</td>'
                f'<td><span class="pill h-{h}">{HEALTH_LABEL[h]}</span></td>'
                "</tr>")
        sections.append(
            f'<section class="team"><h2>{esc(tname)} <span class="count">{len(team_rows)}</span></h2>'
            '<div class="tablewrap"><table><thead><tr><th>Agent</th><th>When (Mountain)</th>'
            '<th>Last run</th><th>Health</th></tr></thead><tbody>' + "".join(trs) + "</tbody></table></div></section>")

    endcard = state.get("endcard") or {}
    endcard_line = ""
    if endcard:
        missing = endcard.get("missing", 0)
        endcard_line = (f'<div class="fig"><div class="num">{missing}</div><div class="lbl">clips in the posting library '
                        f'without the end card ({endcard.get("checked", "?")} checked)</div></div>')

    retired = "".join(f'<li><b>{esc(r["name"])}</b>: {esc(r["why"])}</li>' for r in roster.get("retired", []))
    attn_html = "".join(f"<li>{esc(x)}</li>" for x in attention)

    page = TEMPLATE.format(
        headline=esc(headline),
        checked=esc(checked_local.strftime("%a %b %-d, %-I:%M %p").replace("AM", "am").replace("PM", "pm")),
        total=len(agents),
        on_time=on_time,
        working=len(working),
        trouble=len(trouble),
        building=counts["building"],
        endcard_fig=endcard_line,
        band="".join(svg),
        week="".join(week_html),
        look=("<ul class=look>" + "".join(look) + "</ul>") if look else
             '<p class="calm">Nothing is late or failing.</p>',
        attention=(f'<div class="ask"><h3>Only Alan can do</h3><ul>{attn_html}</ul></div>' if attention else ""),
        sections="".join(sections),
        limits=esc(roster.get("hardLimits", "")),
        retired=retired,
    )
    summary = f"{on_time}/{len(working)} on schedule, {len(trouble)} need a look, {counts['building']} being built"
    return page, summary, trouble


TEMPLATE = """<title>Agent Workforce</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
/* VOICE work: an ops board for a two-founder company run by agents
   IDEA the dispatch board in an equipment yard: every crew, its shift, a lamp for how it went
   PICTURE a 24-hour band (Mountain time) with a tick for every daily run, coloured by health, plus a week strip
   COLOUR white ground, slate ink, YardSwaps blue leads; green, amber, red only on lamps
   TYPE Space Grotesk display + Inter text
   LAYOUT laptop: headline and four figures across the top, band full width under it; phone: stacked, band scrolls inside its box */
:root{{--bg:#FFFFFF;--panel:#F6F6F8;--line:#D8D8DA;--ink:#1A3353;--text:#202020;--muted:#545456;--blue:#2563EB;
--ok:#0B7A1F;--late:#A16207;--bad:#C81E1E;--grey:#8A8A8E;--sched:#2563EB;--lane:#F1F4FA;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0E1726;--panel:#152238;--line:#2A3A55;--ink:#E6ECF5;
--text:#E6ECF5;--muted:#A8B3C4;--blue:#6E9BFF;--ok:#4CC26A;--late:#E0A43A;--bad:#FF6B6B;--grey:#7D8798;--sched:#6E9BFF;--lane:#17263D;}}}}
:root[data-theme="dark"]{{--bg:#0E1726;--panel:#152238;--line:#2A3A55;--ink:#E6ECF5;--text:#E6ECF5;--muted:#A8B3C4;
--blue:#6E9BFF;--ok:#4CC26A;--late:#E0A43A;--bad:#FF6B6B;--grey:#7D8798;--sched:#6E9BFF;--lane:#17263D;}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--text);font:15px/1.5 Inter,-apple-system,"Segoe UI",sans-serif;margin:0}}
.wrap{{max-width:1240px;margin:0 auto;padding-block:28px 48px;padding-left:max(5vw,16px,env(safe-area-inset-left,0px));padding-right:max(5vw,16px,env(safe-area-inset-right,0px))}}
.top{{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:28px;align-items:end}}
.kicker{{font:600 13px Inter,sans-serif;color:var(--blue);letter-spacing:.01em;margin:0 0 6px}}
h1{{font:700 40px/1.05 "Space Grotesk",Inter,sans-serif;letter-spacing:-.02em;color:var(--ink);margin:0}}
.sub{{color:var(--muted);margin:10px 0 0}}
.figs{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}
.fig{{border-top:3px solid var(--blue);padding-top:8px;min-width:0}}
.fig .num{{font:700 32px/1 "Space Grotesk",sans-serif;color:var(--ink)}}
.fig .lbl{{font-size:13px;color:var(--muted)}}
.fig.warn{{border-color:var(--late)}}
.board{{margin-top:26px;border:1px solid var(--line);border-radius:14px;padding:16px 16px 10px;background:var(--bg)}}
.board h2,.team h2,.side h2{{font:700 20px/1.2 "Space Grotesk",sans-serif;color:var(--ink);margin:0 0 10px;letter-spacing:-.01em}}
.bandwrap{{overflow-x:auto}}
.band{{width:100%;min-width:720px;height:auto;display:block}}
.band .grid{{stroke:var(--line);stroke-width:1}}
.band .axis{{fill:var(--muted);font:500 12px Inter,sans-serif}}
.band .lane{{fill:var(--lane)}}
.band .lanelabel{{fill:var(--ink);font:600 13px Inter,sans-serif;opacity:.85}}
.band .now{{stroke:var(--ink);stroke-width:1.5;stroke-dasharray:3 3}}
.band .nowlabel{{fill:var(--ink);font:600 12px Inter,sans-serif}}
.tick rect{{fill:var(--grey)}} .tick.h-ok rect{{fill:var(--blue)}} .tick.h-late rect{{fill:var(--late)}}
.tick.h-failed rect,.tick.h-needs_alan rect{{fill:var(--bad)}} .tick.h-building rect{{fill:var(--grey);opacity:.5}}
.swipe{{display:none;margin:4px 0 0}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--muted);margin:8px 0 2px}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.legend i{{width:10px;height:10px;border-radius:3px;display:inline-block}}
.split{{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:20px;margin-top:20px}}
.weekly{{margin-top:28px}} .weekly h2{{font:700 20px/1.2 "Space Grotesk",sans-serif;color:var(--ink);margin:0 0 10px}}
.endcard .fig{{border-color:var(--ok)}}
.week{{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px}}
.day{{background:var(--panel);border-radius:10px;padding:8px;min-width:0}}
.dayname{{font:700 14px "Space Grotesk",sans-serif;color:var(--ink);margin-bottom:6px}}
.chip{{font-size:12.5px;line-height:1.25;display:flex;gap:6px;align-items:flex-start;margin-bottom:6px;overflow-wrap:anywhere}}
.chip.empty{{color:var(--muted)}}
.lamp{{width:10px;height:10px;border-radius:50%;flex:none;margin-top:3px;background:var(--grey)}}
.h-ok .lamp,.lamp.h-ok{{background:var(--ok)}} .h-late .lamp,.lamp.h-late{{background:var(--late)}}
.h-failed .lamp,.lamp.h-failed,.h-needs_alan .lamp,.lamp.h-needs_alan{{background:var(--bad)}}
.h-scheduled .lamp,.lamp.h-scheduled{{background:var(--sched)}}
.lamp.h-building{{background:transparent;border:2px solid var(--grey)}}
.side{{background:var(--panel);border-radius:14px;padding:16px;min-width:0}}
.look{{list-style:none;padding:0;margin:0}} .look li{{margin:0 0 10px}}
.calm{{margin:0;color:var(--muted)}}
.ask{{margin-top:14px;border-top:1px solid var(--line);padding-top:12px}}
.ask h3{{font:700 15px "Space Grotesk",sans-serif;margin:0 0 6px;color:var(--ink)}}
.ask ul{{margin:0;padding-left:18px}}
.pill{{display:inline-block;font:600 12px Inter,sans-serif;padding:2px 8px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}}
.pill.h-ok{{color:var(--ok)}} .pill.h-late{{color:var(--late)}} .pill.h-failed,.pill.h-needs_alan{{color:var(--bad)}}
.pill.h-building,.pill.h-nosignal{{color:var(--muted)}} .pill.h-scheduled{{color:var(--sched)}}
.muted{{color:var(--muted);font-size:13px}}
.team{{margin-top:28px}}
.count{{font:500 14px Inter,sans-serif;color:var(--muted);margin-left:4px}}
.tablewrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px}}
table{{border-collapse:collapse;width:100%;min-width:720px}}
th{{text-align:left;font:600 13px Inter,sans-serif;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--line);background:var(--panel)}}
td{{padding:12px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:last-child td{{border-bottom:0}}
td.agent{{width:46%}} .who{{display:flex;gap:10px}}
.who .lamp{{margin-top:6px}}
.does{{color:var(--muted);font-size:13.5px;margin-top:2px}}
.foot{{margin-top:32px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}}
.foot .box{{border-left:3px solid var(--ink);padding:2px 0 2px 14px}}
.foot h3{{font:700 16px "Space Grotesk",sans-serif;margin:0 0 6px;color:var(--ink)}}
.foot ul{{margin:0;padding-left:18px}}
@media (max-width:860px){{.swipe{{display:block}} .top,.split,.foot{{grid-template-columns:minmax(0,1fr)}} .figs{{grid-template-columns:repeat(2,minmax(0,1fr))}}
h1{{font-size:32px}} .week{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
</style>
<div class="wrap">
  <div class="top">
    <div>
      <p class="kicker">YardSwaps agent workforce · checked {checked} Mountain</p>
      <h1>{headline}</h1>
      <p class="sub">Every agent that runs the company, when it works and how its last shift went. Rebuilt by the Roster Keeper at about 6 am and 5 pm Mountain.</p>
    </div>
    <div class="figs">
      <div class="fig"><div class="num">{total}</div><div class="lbl">agents on the roster</div></div>
      <div class="fig"><div class="num">{on_time}/{working}</div><div class="lbl">working agents on schedule</div></div>
      <div class="fig warn"><div class="num">{trouble}</div><div class="lbl">late, failed or waiting on Alan</div></div>
      <div class="fig"><div class="num">{building}</div><div class="lbl">being built (Studio)</div></div>
    </div>
  </div>

  <div class="board">
    <h2>Today's shifts, Mountain time</h2>
    <div class="bandwrap">{band}</div>
    <p class="swipe muted">Swipe the band to see the whole day.</p>
    <div class="legend"><span><i style="background:var(--blue)"></i>ran on schedule</span><span><i style="background:var(--late)"></i>late</span><span><i style="background:var(--bad)"></i>failed or needs Alan</span><span><i style="background:var(--grey)"></i>no signal yet or being built</span></div>
  </div>

  <div class="split">
    <div class="side"><h2>Needs a look</h2>{look}{attention}</div>
    <div class="side endcard">{endcard_fig}</div>
  </div>

  <section class="weekly"><h2>Weekly crews</h2>{week}</section>

  {sections}

  <div class="foot">
    <div class="box"><h3>Hard limits for every agent</h3><p style="margin:0">{limits}</p></div>
    <div class="box"><h3>Paused on purpose</h3><ul>{retired}</ul></div>
  </div>
</div>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", default=str(HERE / "roster.json"))
    ap.add_argument("--state", default=str(HERE / "logs" / "roster-state.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--now", help="ISO time to render as now (tests)")
    args = ap.parse_args()
    roster = json.loads(Path(args.roster).read_text())
    state_path = Path(args.state)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    now = parse_iso(args.now) if args.now else dt.datetime.now(dt.timezone.utc)
    page, summary, trouble = build(roster, state, now)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(summary)
    for a, seen, h in trouble:
        print(f"- {HEALTH_LABEL[h]}: {a['name']} ({a.get('owner')}) {seen.get('note') or ''}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())

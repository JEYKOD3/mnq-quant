"""Render knowledge/BACKTEST_2026_YTD.md from knowledge/src/y2026_summary.json (+ caps.json, d2_final.json)."""
import json
J = json.load(open('/home/claude/mnq-quant/knowledge/src/y2026_summary.json'))
B = J['brief']; P = J['prop']; EV = J['evening']; SDH = J['stopday']
STR = ['NEWS', 'V4+', 'D2', 'TDP', 'Pinball', 'H2', 'TEAM']
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
def m(x): return f"{x:,}" if isinstance(x, int) else str(x)
def hm(x): x = int(x); return f"{x // 60}:{x % 60:02d}"
def pct(x): return f"{x * 100:.0f}%" if x is not None else 'n/a'
def dt(d): d = str(d); return f"{d[4:6]}/{d[6:]}"
L = []
A = L.append
DESC = {
 'NEWS': "Unchanged and flat by 10:30. Small, steady: 15 trades, two-thirds winners, at most 2 losses in a row this year. At engine size it is the most efficient module because its 50 pt stop allows 9 to 10 MNQ.",
 'V4+': "The 2026 workhorse. The 15:00 hard exit (was 15:55) lifts 2026 from $1,821 to $2,578 at 1 MNQ. 2022 improves (+$305) and 2023-25 are within $230 of the old rule. It struggled in August and September (choppy, -$544 combined), then came back in October (+$879).",
 'D2': "New rule: 0.6 ADR threshold, exit 13:15. Fewer trades (36 vs 50) and a much smaller drawdown ($985 vs $1,571). It depends on a few big trend days: June alone (+$2,303) is most of the year. It loses in choppy months (Apr, Jul, Aug). In 2024-25 it is only breakeven at 1 MNQ.",
 'TDP': "Needs real trend days: strong March to June, then four losing months in a row (Jul to Oct) when trend days with clean pullbacks dried up. The 15:00 exit costs almost nothing ($1,510 vs $1,553) and keeps PF 1.5.",
 'Pinball': "The weakest module in 2026 (PF 1.16, 13 trades). One great March, a bad April, nothing in June or September. Its big edge in 2022-25 came from long holds, so the 3-hour cap and 2R target cut 2022 roughly in half. Treat it as a low-weight diversifier.",
 'H2': "Quietly the best 2026 risk-adjusted module (PF 2.31, drawdown $396), at half size. 2022-25 is only slightly positive, so most of the 2026 result is regime. With the 15:00 exit nothing changes except one trade.",
 'TEAM': "Best months March, June and October (trend months). Worst stretch July-August, when trend-following setups lost together. NEW is better than OLD on 2026 at 1 MNQ (+$1,630, PF 1.74 vs 1.43, drawdown -$456), but gives back $500 to $3,250 a year in 2022-25.",
}
A("# MNQ day engine: 2026 YTD backtest, old vs new rules (Oct 25 2026)")
A("")
A(f"Data: MNQ RTH 1m (Databento to 2026-10-20, plus TradingView bars to {dt(J['meta']['data_end'])}), 2026-01-02 to 2026-{dt(J['meta']['data_end']).replace('/', '-')}, {J['meta']['days2026']} trading days. Per-year tables cover 2022-2026. Selection windows: 2026 + 2025 are primary (the closest regime twins), 2022 is the second check (big gaps and volatility), and 2023-24 are the calm-regime stress test.")
A("")
A("Costs: 1 MNQ figures pay $2.37 per side commission plus 1 tick slippage on entries and stop exits. Engine figures use the live sizing (65% of room above the max-loss line, $1,100 shared daily budget, H2 half size, D2 half size against the daily trend) and the existing +8 pt stop slippage convention. Same-minute signals are sized in Pine script order (NEWS, V4+, D2, TDP, Pinball, H2).")
A("")
A("## 1. Rule sets")
A("")
A("**OLD** (live Pine v6): NEWS 50/50 flat 10:30 | V4+ 1.25R, breakeven at +1R, flat 15:55 | D2 0.5 ADR, exit 15:00 | TDP 1.5R, flat 15:55 | Pinball no target, flat 15:55 | H2 2R, 3/day, flat 15:55.")
A("")
A("**NEW** (recommended, nothing open after 15:00):")
A("")
A("| Strategy | Change | Exact rule |")
A("|---|---|---|")
A("| NEWS | none | 8:30 reversion, stop 50 / target 50 pts, flat 10:30 |")
A("| V4+ | hard flat 15:00 | 1.25R target, stop to entry +1.25 pt at +1R, entries 9:45-13:00, flat 15:00 |")
A("| D2 | threshold 0.6, exit 13:15 | at 10:29 close, \\|close - open\\| >= 0.6 ADR, market at 10:30, stop = open -/+ 1 tick, no target, flat 13:15 (see D2_EXITS_2026.md) |")
A("| TDP | hard flat 15:00 | unchanged entry (limit at 1/3 first-hour range pullback until 12:00), stop 0.4 ADR, 1.5R target, flat 15:00 |")
A("| Pinball | 2R target, 180 min cap, flat 15:00 | unchanged entry (break of first-hour extreme after 3-day RSI extreme, with trend), stop other side of the first hour, 2R target, exit 180 min after entry or 15:00, whichever is first |")
A("| H2 | hard flat 15:00 | 2R target, max 3/day, half size, last entry 14:55, flat 15:00 |")
A("| Day engine | stop-day rule | no new entries once (a) realized loss >= $950, (b) room above the max-loss line < $400, (c) 3 losing trades today, or (d) the eval is passed (target reached AND best day <= 40% of profit) |")
A("")
A("### Priority 2: why these caps")
A("")
A("Grid: targets x time caps (60-240 min) x hard flat 13:00 / 14:00 / 15:00 / 15:55, each variant swapped into the team (new D2, other strategies live) and scored on the 40-day pass rate (`scripts/y2026/caps.py`, `caps.json`).")
A("")
C = json.load(open('/home/claude/mnq-quant/scripts/y2026/caps.json'))
def crow(s, kw, lab):
    r = [x for x in C if x['s'] == s and x['kw'] == kw][0]
    y = r['yr']; e = r['ev']
    return f"| {lab} | " + ' | '.join(f"{y[str(k)]['net']:,}" for k in range(2022, 2027)) + f" | {y['2026']['hold']} | " + ' | '.join(f"{pct(e[w]['p40'])} / {e[w]['fail'] * 100:.0f}%" for w in ('2026', '2025', '2022', '2023-24')) + " |"
A("| Variant | 2022 $ | 2023 $ | 2024 $ | 2025 $ | 2026 $ | 2026 hold (min) | eval 2026 | eval 2025 | eval 2022 | eval 2023-24 |")
A("|---|---|---|---|---|---|---|---|---|---|---|")
for s, kw, lab in (('V4+', {'cap': 0, 'flat': 955}, 'V4+ live, flat 15:55'), ('V4+', {'cap': 0, 'flat': 900}, '**V4+ flat 15:00**'), ('V4+', {'cap': 0, 'flat': 840}, 'V4+ flat 14:00'), ('V4+', {'cap': 120, 'flat': 900}, 'V4+ 120 min cap'),
                   ('Pinball', {'tgtR': None, 'cap': 0, 'flat': 955}, 'Pinball live, flat 15:55'), ('Pinball', {'tgtR': 2, 'cap': 180, 'flat': 900}, '**Pinball 2R, 180 min, flat 15:00**'), ('Pinball', {'tgtR': None, 'cap': 180, 'flat': 900}, 'Pinball no target, 180 min, 15:00'), ('Pinball', {'tgtR': 2, 'cap': 0, 'flat': 840}, 'Pinball 2R, flat 14:00'),
                   ('TDP', {'tgtR': 1.5, 'cap': 0, 'flat': 955}, 'TDP live, flat 15:55'), ('TDP', {'tgtR': 1.5, 'cap': 0, 'flat': 900}, '**TDP 1.5R, flat 15:00**'), ('TDP', {'tgtR': 1.5, 'cap': 0, 'flat': 840}, 'TDP 1.5R, flat 14:00'), ('TDP', {'tgtR': 1.5, 'cap': 180, 'flat': 900}, 'TDP 180 min cap'),
                   ('H2', {'tgtR': 2, 'cap': None, 'flat': 955}, 'H2 live, flat 15:55'), ('H2', {'tgtR': 2, 'cap': None, 'flat': 900}, '**H2 2R, flat 15:00**'), ('H2', {'tgtR': 2, 'cap': None, 'flat': 840}, 'H2 2R, flat 14:00'), ('H2', {'tgtR': 1.5, 'cap': 90, 'flat': 840}, 'H2 1.5R, 90 min, 14:00')):
    A(crow(s, kw, lab))
A("")
A("Eval cells are pass within 40 days / fail, 40% consistency.")
A("")
A("- **V4+:** 15:00 is the only earlier exit that does not hurt. 14:00 and the 2-3 hour caps cut the 2026 pass rate by 7 to 17 points, because V4+ winners often need the afternoon to reach 1.25R.")
A("- **Pinball:** the 180 min cap plus a 15:00 flat raises the 2026 pass rate from 33% to 38% and removes the 15:55 holds. The 2R target only adds 2025 money. 2022 at 1 MNQ halves ($4,115 to $2,110), the price of leaving early.")
A("- **TDP:** 15:00 is best on 2026 + 2025. 14:00 is the safer fallback (0% vs 6% fails in 2022, but $180 to $880 less a year at 1 MNQ).")
A("- **H2:** the faster exits (1.5R, 90 min, 14:00) look better in the eval but lose money in 4 of 5 years at 1 MNQ, so they are rejected. Keep 2R and just flatten at 15:00.")
A("- **The high first-hour share supports earlier exits only for D2, and only down to about 13:15.** Below that, every strategy loses edge in 2025 and 2026.")
A("")
A("## 2. 2026 YTD brief per strategy")
A("")
for k in ('OLD', 'NEW'):
    A(f"### {k} rules, 2026 YTD")
    A("")
    A("| Strategy | Trades | Wins | Win % | PF | Net 1 MNQ | Net engine* | Avg win | Avg loss | Max DD 1 MNQ | Best day | Worst day | Longest losing streak | Avg hold | Latest exit (1m bar) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in STR:
        v = B[k][s]
        A(f"| {s} | {v['n']} | {v['wins']} | {pct(v['win'])} | {v['pf']} | {v['net1']:,} | {v['neteng']:,} | {v['avgw']} | {v['avgl']} | {v['dd']:,} | {v['best']:,} ({dt(v['bestd'])}) | {v['worst']:,} ({dt(v['worstd'])}) | {v['streak']} | {v['hold']} min | {hm(v['last_exit'] - (1 if k == 'NEW' and s != 'NEWS' else 0))} |")
    A("")
A("*Net engine: each day sized as on a fresh eval with $2,000 of room, all strategies sharing the $1,100 budget, +8 pt stop slippage. It shows how the sizing tilts the results (NEWS and H2 get many contracts, D2 gets about 1), not an account curve.")
A("")
A("### Monthly net, 1 MNQ")
A("")
for k in ('OLD', 'NEW'):
    A(f"**{k}**")
    A("")
    A("| Strategy | " + ' | '.join(MON) + " |")
    A("|---|" + "---|" * len(MON))
    for s in STR:
        A(f"| {s} | " + ' | '.join(f"{B[k][s]['mon'][mm]:,}" for mm in MON) + " |")
    A("")
A("### Per year, 1 MNQ (net $ / PF)")
A("")
A("| Strategy | Rules | 2022 | 2023 | 2024 | 2025 | 2026 YTD |")
A("|---|---|---|---|---|---|---|")
for s in STR:
    for k in ('OLD', 'NEW'):
        y = B[k][s]['yr']
        A(f"| {s} | {k} | " + ' | '.join(f"{y[str(t)]['net']:,} / {y[str(t)]['pf']}" for t in range(2022, 2027)) + " |")
A("")
A("### How each strategy did in 2026 (new rules)")
A("")
for s in STR: A(f"- **{s}:** {DESC[s]}")
A("")
A("### Optional evening modules (separate budget, 1 MNQ, 2026 YTD)")
A("")
A("The trader trades evenings only from 18:00 to 20:00 ET, on a separate budget handled by another agent. These numbers are for reference only.")
A("")
A("| Module | Trades | Wins | Win % | PF | Net | Avg win | Avg loss | Max DD | Best | Worst | Losing streak | 2022 | 2023 | 2024 | 2025 |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k, v in EV.items():
    A(f"| {k} | {v['n']} | {v['wins']} | {pct(v['win'])} | {v['pf']} | {v['net1']:,} | {v['avgw']} | {v['avgl']} | {v['dd']:,} | {v['best']} | {v['worst']} | {v['streak']} | " + ' | '.join(f"{v['yr'][str(t)]['net']:,} / {v['yr'][str(t)]['pf']}" for t in range(2022, 2026)) + " |")
A("")
A("| Module | " + ' | '.join(MON) + " |")
A("|---|" + "---|" * len(MON))
for k, v in EV.items(): A(f"| {k.split(' (')[0]} | " + ' | '.join(f"{v['mon'][mm]:,}" for mm in MON) + " |")
A("")
A("- **S2 as specified (exit 03:30):** good 2026 (PF 1.64), but all of it comes from June and July, and it had 8 losers in a row. It holds outside the 18:00-20:00 window the trader accepts.")
A("- **S2 cut at 20:00:** fits the window and looks clean in 2026 (PF 2.07, drawdown $574). It loses in 2022 and 2024, so most of the 2026 result is regime. Paper only.")
A("- **Sunday Gap Pullback:** 18 trades, PF 2.68, drawdown $275. It is the best evening candidate for 2026, but slightly negative in 2023 and 2025. Small size, paper first.")
A("")
A("## 3. Stop-day rule test (team eval, 40% consistency)")
A("")
A("| Rules | Stop-day | 2026 | 2025 | 2022 | 2023-24 | net 2026 engine | net 2025 engine |")
A("|---|---|---|---|---|---|---|---|")
for k in ('OLD', 'NEW'):
    for lab, v in SDH[k].items():
        e = v['ev']
        A(f"| {k} | {lab} | " + ' | '.join(f"{pct(e[w]['p40'])} / {e[w]['fail'] * 100:.1f}% / {e[w]['med']}d" for w in ('2026', '2025', '2022', '2023-24')) + f" | {v['net']['2026']:,} | {v['net']['2025']:,} |")
A("")
A("Cells: pass within 40 days / fail / median days to pass.")
A("")
A("- **Rule (c) (N losing trades) never binds for N = 2, 3 or 4.** In 2022-2026 only 2 entries came after 2 closed losses, and the $1,100 budget had already sized both at 0. Rules (a) and (b) are also covered by the budget. N = 1 changes little (+2 points in 2026, -1 in 2023-24).")
A("- **Rule (d) does the work.** Stopping new entries once the eval is passed protects the passing day: +4 to +6 points of pass rate in 2026 and 2025.")
A("- **(d) must mean \"passed\", not \"target reached\".** With the 40% consistency rule, \"stop at $3,000\" freezes accounts that are over target but not yet consistent (\"naive (d)\" rows: -9 to -17 points).")
A("- **Recommendation:** keep N = 3 as a harmless safety net, and code (d) as \"target reached and best day <= 40% of total profit\".")
A("")
A("## 4. Prop-firm validation, 2026 only")
A("")
A("Lucid Flex 50K: $3,000 target, $2,000 end-of-day trailing max loss, mll = min(peakEOD - 2000, 50,100), 40% consistency (50% shown for reference), flat by 16:45 (the engine is flat by 15:00).")
A("")
A("### (i) Rolling start every 2026 trading day (210 starts, run until data end)")
A("")
A("| Rules | Consistency | Stop-day | Pass <= 40d | Pass by data end | Fail | Still open | Median days to pass | Worst DD from start | Median worst DD | Runs blocked by consistency | Extra days needed (median / max) |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|")
for k in ('OLD', 'NEW'):
    for c in (40, 50):
        for sd in ('None', '3'):
            v = P[k][f'roll cons{c} sd{sd}']
            A(f"| {k} | {c}% | {'off' if sd == 'None' else 'N=3'} | {pct(v['p40'])} | {pct(v['p'])} | {v['f'] * 100:.1f}% | {pct(v['o'])} | {v['med']} | {v['worst']:,} | {v['worst_med']:,} | {v['cons_hit']} ({pct(v['cons_hit_pct'])} of runs that hit $3,000) | {v['extra_med']} / {v['extra_max']} |")
A("")
A("- **Still open** is high because starts after August have little data left, and some runs sit over target waiting for consistency. Of the runs that ended, NEW passed 100% with the stop-day rule on.")
A("- **Consistency is the main brake.** Without the stop-day rule, 69-72% of runs that reach $3,000 are blocked by one big day, and need a median 5 (NEW) to 10 (OLD) extra trading days. The stop-day rule's pass check cuts that to 38% of runs for NEW.")
A("")
A("### (ii) Monte Carlo: 10,000 bootstrapped 40-day evals from 2026 trading days")
A("")
A("| Rules | Consistency | Stop-day | Pass | Fail | Open after 40 days | Median days to pass |")
A("|---|---|---|---|---|---|---|")
for k in ('OLD', 'NEW'):
    for c in (40, 50):
        for sd in ('None', '3'):
            v = P[k][f'mc cons{c} sd{sd}']
            A(f"| {k} | {c}% | {'off' if sd == 'None' else 'N=3'} | {pct(v['p'])} | {v['f'] * 100:.1f}% | {pct(v['o'])} | {v['med']} |")
A("")
A("### (iii) Stress (rolling 2026, 40% consistency, stop-day N=3)")
A("")
A("| Scenario | OLD pass <= 40d | OLD fail | NEW pass <= 40d | NEW fail | NEW median days |")
A("|---|---|---|---|---|---|")
rows = [('Base (+8 pt stop slip, $4.74 RT)', 'roll cons40 sd3'), ('+1 pt per side (entries and stop exits)', 'stress +1pt'), ('+2 pt per side', 'stress +2pt'), ('+4 pt per side', 'stress +4pt'),
        ('Only 1 tick slippage (no +8 pt)', 'stress 1-tick only (no +8 stop slip)'), ('Commission $1.00 RT', 'comm $1.00 RT')]
for lab, key in rows:
    o = P['OLD'][key]; n = P['NEW'][key]
    A(f"| {lab} | {pct(o['p40'])} | {o['f'] * 100:.1f}% | {pct(n['p40'])} | {n['f'] * 100:.1f}% | {n['med']} |")
o = P['OLD']['skip 20%']; n = P['NEW']['skip 20%']
A(f"| Skip 20% of signals at random (100 runs: mean, 5th pct) | {pct(o['p40'])} ({pct(o['p40_lo'])}) | {o['f'] * 100:.1f}% | {pct(n['p40'])} ({pct(n['p40_lo'])}) | {n['f'] * 100:.1f}% | {n['med']} |")
A("")
A("- **Extra slippage up to +2 pts barely moves the pass rate.** Cells move by a point or two either way, because smaller winning days also help the consistency rule. +4 pts costs 6 to 7 points for both rule sets.")
A("- **Missing 20% of trades costs about 8-9 points of pass rate.** A bad draw drops it to 20%, but fails stay at 0%.")
A("- **No stress scenario produced a failed eval with the stop-day rule on.** The budget and the 65% sizing keep the worst drawdown from start above -$1,970.")
A("")
A("### (iv) Funded phase after the pass (stop-day N=3)")
A("")
A("Lucid Flex funded: 5 days of >= $150 profit per cycle plus positive profit, then request min(50% of profit, $2,000), minimum $500, 90% to the trader. A request moves the floor to $50,100 at once. Policy A requests as soon as allowed. Policy B waits until $1,100 of room would remain above $50,100 after the request.")
A("")
A("| Rules | Policy | Sample | Got >= 1 payout | Median days to 1st payout | Payouts per account | Avg paid to trader | Median payout | Bust |")
A("|---|---|---|---|---|---|---|---|---|")
for k in ('OLD', 'NEW'):
    for pol in ('funded A (request asap)', 'funded B (keep $1,100 room)'):
        for smp, lab in (('mc120', 'Monte Carlo, 120 days'), ('hist', 'chained from 2026 passes (truncated at data end)')):
            v = P[k][pol][smp]
            A(f"| {k} | {pol.split(' (')[0][-1]} | {lab} (n {v['n']}) | {pct(v['got_pay'])} | {v['first_med']} | {v['pays_avg']} | ${v['trader_avg']:,} | ${round(v['pay_med'] or 0):,} | {v['bust'] * 100:.1f}% |")
A("")
A("- **The real constraint in funded is the 50% / $2,000 cap.** The first request usually comes 18-19 trading days after funding. Payouts run $1,500-2,000, about 1.5 payouts per 120 days with the new rules.")
A("- **Policy B** pays less often but in bigger amounts, about the same money (+$260 over 120 days with NEW). Its value is the cushion after the floor jumps to $50,100. Both policies had essentially 0% busts in the 2026 bootstrap.")
A("")
A("## 5. Verdict")
A("")
A("- **On 2026 the new rules are better at 1 MNQ** (+$1,630, PF 1.74 vs 1.43, max drawdown $2,099 vs $2,555). With the stop-day rule they are also better in the 2026 eval: 43% vs 41% pass within 40 days, median 20 vs 23 days, 0% fails.")
A("- **On 2025 and 2022 the new rules pass more often** (48% vs 34% and 48% vs 42% with the stop-day rule). 2023-24 is level (29% vs 27%).")
A("- **The cost of leaving early is lower 1 MNQ profit in older years:** 2022 -$3,250, 2023 -$1,900, 2024 -$900, 2025 -$500. Most of it is D2 and Pinball giving up the afternoon drift. That is the price of no afternoon holds.")
A("- **The stop-day rule matters only through (d).** Code it as \"passed\" (target and 40% consistency both met), not \"target reached\".")
A("- **Biggest risks:** small 2026 samples (Pinball 13 trades, D2 36), and July-August-style chop, when V4+, TDP and D2 lose together. A 20% miss rate on signals costs about 8 points of pass rate.")
A("")
A("Scripts: `scripts/y2026/common.py` (engine), `rulesets.py`, `d2_grid.py`, `d2_team.py`, `d2_exit_time.py`, `d2_scan2.py`, `d2_final.py`, `caps.py`, `report.py`, `gen_md.py`. Data for charts: `knowledge/src/y2026_summary.json`.")
open('/home/claude/mnq-quant/knowledge/BACKTEST_2026_YTD.md', 'w').write('\n'.join(L) + '\n')
print(len(L))

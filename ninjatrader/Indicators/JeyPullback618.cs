// JeyPullback618 - NinjaTrader 8 indicator (MNQ 1-minute chart)
// Core setup (tested 5y RTH 1m: PF 1.34, every year >= 1.22; Oct 19-23: 1.13/1.29, Oct 26-30: 1.81/1.88 shorts/longs):
//   Leg: A = highest high (shorts) of the last Lookback bars, B = lowest low after A, leg = A-B >= LegMin points.
//   Setup when price has bounced >= BounceFrac of the leg off B AND the 5-minute EMA21 slopes in the leg direction (30 min).
//   Entry: limit at B + Fib x leg. Stop: A + 2 pts (beyond the lower high). Target: 80% of the way from entry to B (Lucid MC: same pass rate, fewer fails than B). Cancel on a new low below B or after 60 bars.
//   Size: floor(RiskUsd / (stop distance x $2)).
// Optional (current-regime only, NOT a long-run edge): exhaustion arrows on 5m closes
//   Sell: 60-min change > 1.6 ATR, RSI > 59, in the top 42% of the 4h range. Buy: 30-min change < -1.34 ATR, volume z > 0.72, RSI < 39, bottom 17% of the 60-min range.
#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class JeyPullback618 : Indicator
    {
        private EMA ema5;
        private ATR atr5;
        private RSI rsi5;
        private SMA volMean5;
        private StdDev volStd5;
        private int shortKey = -1, longKey = -1;          // absolute bar index of leg start A (one setup at a time per side)
        private int shortBorn = -1, longBorn = -1;
        private int pendingExh = 0;                        // set on a 5m close, drawn on the next 1m bar

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Pullback 61.8 into a 60+ pt leg with 5m trend filter; entry, stop, target and size drawn on the chart.";
                Name = "JeyPullback618";
                Calculate = Calculate.OnBarClose;
                IsOverlay = true;
                DisplayInDataBox = false;
                DrawOnPricePanel = true;
                IsSuspendedWhileInactive = true;
                LegMin = 60; Fib = 0.618; Lookback = 120; BounceFrac = 0.3; MaxBarsActive = 60;
                RiskUsd = 300; PointValue = 2; StopBuffer = 2; TargetFrac = 0.8;
                ShowExhaustion = true; AlertsOn = true;
            }
            else if (State == State.Configure)
            {
                AddDataSeries(BarsPeriodType.Minute, 5);
            }
            else if (State == State.DataLoaded)
            {
                ema5 = EMA(BarsArray[1], 21);
                atr5 = ATR(BarsArray[1], 14);
                rsi5 = RSI(BarsArray[1], 14, 1);
                volMean5 = SMA(Volumes[1], 48);
                volStd5 = StdDev(Volumes[1], 48);
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress == 1)
            {
                if (CurrentBars[1] < 60 || !ShowExhaustion) return;
                double a = atr5[0];
                if (a <= 0) return;
                double r12 = (Closes[1][0] - Closes[1][12]) / a;
                double r6 = (Closes[1][0] - Closes[1][6]) / a;
                double hi48 = MAX(Highs[1], 48)[0], lo48 = MIN(Lows[1], 48)[0];
                double hi12 = MAX(Highs[1], 12)[0], lo12 = MIN(Lows[1], 12)[0];
                double pos48 = (Closes[1][0] - lo48) / Math.Max(hi48 - lo48, TickSize);
                double pos12 = (Closes[1][0] - lo12) / Math.Max(hi12 - lo12, TickSize);
                double volz = volStd5[0] > 0 ? (Volumes[1][0] - volMean5[0]) / volStd5[0] : 0;
                if (r12 > 1.6 && rsi5[0] > 59 && pos48 > 0.58) pendingExh = -1;
                else if (r6 < -1.34 && volz > 0.72 && rsi5[0] < 39 && pos12 < 0.17) pendingExh = 1;
                return;
            }

            if (CurrentBars[0] < Lookback + 2 || CurrentBars[1] < 30) return;

            if (pendingExh != 0)
            {
                string t = "exh" + CurrentBar;
                if (pendingExh < 0) Draw.ArrowDown(this, t, false, 0, High[0] + 6 * TickSize, Brushes.Orange);
                else Draw.ArrowUp(this, t, false, 0, Low[0] - 6 * TickSize, Brushes.DeepSkyBlue);
                if (AlertsOn) Alert("exh" + CurrentBar, Priority.Medium, pendingExh < 0 ? "Exhaustion SELL (regime play, half size)" : "Exhaustion BUY (regime play, half size)", "", 10, Brushes.Black, Brushes.Orange);
                pendingExh = 0;
            }

            double slope = ema5[0] - ema5[6];
            DoSide(-1, slope);
            DoSide(1, slope);
        }

        private void DoSide(int side, double slope)
        {
            string p = side < 0 ? "pbS" : "pbL";
            int aAgo = side < 0 ? HighestBar(High, Lookback + 1) : LowestBar(Low, Lookback + 1);
            bool valid = false;
            double A = 0, B = 0, leg = 0, entry = 0, stop = 0;
            if (aAgo >= 2)
            {
                A = side < 0 ? High[aAgo] : Low[aAgo];
                int bAgo = side < 0 ? LowestBar(Low, aAgo) : HighestBar(High, aAgo);
                B = side < 0 ? Low[bAgo] : High[bAgo];
                leg = side < 0 ? A - B : B - A;
                if (bAgo >= 1 && leg >= LegMin)
                {
                    double bounce = side < 0 ? MAX(High, bAgo)[0] - B : B - MIN(Low, bAgo)[0];
                    bool trendOk = side < 0 ? slope < 0 : slope > 0;
                    entry = side < 0 ? B + Fib * leg : B - Fib * leg;
                    stop = side < 0 ? A + StopBuffer : A - StopBuffer;
                    bool notThrough = side < 0 ? High[0] < stop : Low[0] > stop;
                    if (bounce >= BounceFrac * leg && trendOk && notThrough) valid = true;
                }
            }

            int key = valid ? CurrentBar - aAgo : -1;
            int curKey = side < 0 ? shortKey : longKey;
            int born = side < 0 ? shortBorn : longBorn;

            if (!valid || (curKey >= 0 && key != curKey) || (born >= 0 && CurrentBar - born > MaxBarsActive))
            {
                if (curKey >= 0) { RemoveDrawObject(p + "E"); RemoveDrawObject(p + "S"); RemoveDrawObject(p + "T"); RemoveDrawObject(p + "X"); }
                if (side < 0) { shortKey = -1; shortBorn = -1; } else { longKey = -1; longBorn = -1; }
                if (!valid || (born >= 0 && CurrentBar - born > MaxBarsActive && key == curKey)) return;
            }

            if (side < 0 && shortKey < 0) { shortKey = key; shortBorn = CurrentBar; }
            if (side > 0 && longKey < 0) { longKey = key; longBorn = CurrentBar; }

            double tgt = entry + (B - entry) * TargetFrac;
            double riskPts = Math.Abs(stop - entry);
            int qty = (int)Math.Floor(RiskUsd / Math.Max(riskPts * PointValue, 1));
            int startAgo = CurrentBar - key;
            Brush c = side < 0 ? Brushes.OrangeRed : Brushes.LimeGreen;
            Draw.Line(this, p + "E", false, startAgo, entry, 0, entry, c, DashStyleHelper.Solid, 2);
            Draw.Line(this, p + "S", false, startAgo, stop, 0, stop, Brushes.Red, DashStyleHelper.Dash, 1);
            Draw.Line(this, p + "T", false, startAgo, tgt, 0, tgt, Brushes.DodgerBlue, DashStyleHelper.Dash, 1);
            Draw.Text(this, p + "X", (side < 0 ? "SELL LIMIT " : "BUY LIMIT ") + entry.ToString("0.00") + "  stop " + stop.ToString("0.00") + " (" + riskPts.ToString("0") + " pts)  target " + B.ToString("0.00") + "  size " + qty + " MNQ", 0, entry + side * -4 * TickSize, c);

            if (AlertsOn && born < 0)
                Alert(p + key, Priority.High, (side < 0 ? "Pullback 61.8 SHORT: limit " : "Pullback 61.8 LONG: limit ") + entry.ToString("0.00") + ", stop " + stop.ToString("0.00") + ", " + qty + " MNQ", "", 30, Brushes.Black, c);
        }

        #region Properties
        [NinjaScriptProperty][Range(10, 1000)][Display(Name = "Min leg (pts)", Order = 1, GroupName = "Setup")]
        public double LegMin { get; set; }
        [NinjaScriptProperty][Range(0.3, 0.9)][Display(Name = "Entry retracement", Order = 2, GroupName = "Setup")]
        public double Fib { get; set; }
        [NinjaScriptProperty][Range(20, 500)][Display(Name = "Lookback (bars)", Order = 3, GroupName = "Setup")]
        public int Lookback { get; set; }
        [NinjaScriptProperty][Range(0.1, 0.6)][Display(Name = "Bounce to arm (fraction of leg)", Order = 4, GroupName = "Setup")]
        public double BounceFrac { get; set; }
        [NinjaScriptProperty][Range(5, 500)][Display(Name = "Cancel after (bars)", Order = 5, GroupName = "Setup")]
        public int MaxBarsActive { get; set; }
        [NinjaScriptProperty][Range(0, 50)][Display(Name = "Stop buffer beyond A (pts)", Order = 6, GroupName = "Setup")]
        public double StopBuffer { get; set; }
        [NinjaScriptProperty][Range(0.2, 1.0)][Display(Name = "Target (share of the way to B)", Order = 7, GroupName = "Setup")]
        public double TargetFrac { get; set; }
        [NinjaScriptProperty][Range(25, 5000)][Display(Name = "Risk per trade ($)", Order = 1, GroupName = "Size")]
        public double RiskUsd { get; set; }
        [NinjaScriptProperty][Range(0.1, 100)][Display(Name = "$ per point per contract (MNQ=2)", Order = 2, GroupName = "Size")]
        public double PointValue { get; set; }
        [NinjaScriptProperty][Display(Name = "Show exhaustion arrows (regime play)", Order = 1, GroupName = "Extras")]
        public bool ShowExhaustion { get; set; }
        [NinjaScriptProperty][Display(Name = "Alerts", Order = 2, GroupName = "Extras")]
        public bool AlertsOn { get; set; }
        #endregion
    }
}

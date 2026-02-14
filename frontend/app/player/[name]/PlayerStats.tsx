"use client";

import { useState } from "react";

interface PlayerStatsProps {
  playerStats: Record<string, number>;
  playerPercentiles: Record<string, number>;
  getColorClass: (pct: number) => string;
}

export default function PlayerStats({
  playerStats,
  playerPercentiles,
  getColorClass,
}: PlayerStatsProps) {
  const [showOnOffDetails, setShowOnOffDetails] = useState(false);
  const decimalPercentKeys = new Set(["ts_pct", "usg_pct", "efg_pct"]);

  const formatStatValue = (value: number, key: string) => {
    if (!Number.isFinite(value)) return "N/A";
    if (decimalPercentKeys.has(key)) {
      return `${(value * 100).toFixed(1)}%`;
    }
    if (key.endsWith("_on_off_diff")) {
      const rounded = value.toFixed(1);
      return value > 0 ? `+${rounded}` : rounded;
    }
    return value.toFixed(1);
  };

  // Helper for the progress bar background color
  const getBarColorClass = (pct: number) => {
    if (pct >= 80) return "bg-red-500";
    if (pct <= 20) return "bg-blue-500";
    return "bg-gray-500";
  };

  const formatPercentile = (pct: number) => {
    if (!Number.isFinite(pct)) return "N/A";
    return `${Math.round(pct)}%`;
  };

  const getPctValue = (pctKey: string) => {
    const value = playerPercentiles[pctKey];
    return Number.isFinite(value) ? value : 0;
  };

  const statsConfig = [
    { label: "Points per 36", key: "pts", pctKey: "pts_pct" },
    { label: "Assists per 36", key: "ast", pctKey: "ast_pct" },
    { label: "Rebounds per 36", key: "reb", pctKey: "reb_pct" },
    { label: "Steals per 36", key: "stl", pctKey: "stl_pct" },
    { label: "Blocks per 36", key: "blk", pctKey: "blk_pct" },
    { label: "Off Rtg On-Off Diff", key: "off_rating_on_off_diff", pctKey: "off_rating_on_off_diff_pct" },
    { label: "Def Rtg On-Off Diff", key: "def_rating_on_off_diff", pctKey: "def_rating_on_off_diff_pct" },
    { label: "Net Rtg On-Off Diff", key: "net_rating_on_off_diff", pctKey: "net_rating_on_off_diff_pct" },
    { label: "True Shooting %", key: "ts_pct", pctKey: "ts_pct_pct" },
    { label: "Usage %", key: "usg_pct", pctKey: "usg_pct_pct" },
    { label: "Effective FG %", key: "efg_pct", pctKey: "efg_pct_pct" },
  ];

  const onOffDetailConfig = [
    { label: "Off Rtg On Court", key: "off_rating_on_court", pctKey: "off_rating_on_court_pct" },
    { label: "Off Rtg Off Court", key: "off_rating_off_court", pctKey: "off_rating_off_court_pct" },
    { label: "Off Rtg On-Off Diff", key: "off_rating_on_off_diff", pctKey: "off_rating_on_off_diff_pct" },
    { label: "Def Rtg On Court", key: "def_rating_on_court", pctKey: "def_rating_on_court_pct" },
    { label: "Def Rtg Off Court", key: "def_rating_off_court", pctKey: "def_rating_off_court_pct" },
    { label: "Def Rtg On-Off Diff", key: "def_rating_on_off_diff", pctKey: "def_rating_on_off_diff_pct" },
    { label: "Net Rtg On Court", key: "net_rating_on_court", pctKey: "net_rating_on_court_pct" },
    { label: "Net Rtg Off Court", key: "net_rating_off_court", pctKey: "net_rating_off_court_pct" },
    { label: "Net Rtg On-Off Diff", key: "net_rating_on_off_diff", pctKey: "net_rating_on_off_diff_pct" },
  ];

  return (
    <section className="flex-1 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold">Stats & Percentiles</h2>
        <button
          type="button"
          onClick={() => setShowOnOffDetails((prev) => !prev)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {showOnOffDetails ? "Hide On/Off Breakdown" : "Show On/Off Breakdown"}
        </button>
      </div>

      <div className="space-y-4">
        {statsConfig.map((stat) => {
          const value = playerStats[stat.key];
          const pct = playerPercentiles[stat.pctKey]; // 0-100
          const pctValue = getPctValue(stat.pctKey);
          const barWidth = `${pctValue}%`;

          return (
            <div key={stat.key} className="flex items-center gap-3">
              {/* Stat Label */}
              <span className="font-medium w-40">{stat.label}</span>

              {/* Progress Bar */}
              <div className="relative flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColorClass(pctValue)}`}
                  style={{ width: barWidth }}
                />
              </div>

              {/* Stat Value & Percentile */}
              <span className="min-w-[3rem] text-right">{formatStatValue(value, stat.key)}</span>
              <span className={`${getColorClass(pctValue)} font-bold`}>
                {formatPercentile(pct)}
              </span>
            </div>
          );
        })}
      </div>

      {showOnOffDetails && (
        <div className="mt-6 rounded-xl border border-gray-200 p-4 dark:border-gray-700">
          <h3 className="mb-3 text-lg font-semibold">On/Off Deep Dive</h3>
          <div className="space-y-3">
            {onOffDetailConfig.map((stat) => {
              const value = playerStats[stat.key];
              const pct = playerPercentiles[stat.pctKey];
              const pctValue = getPctValue(stat.pctKey);
              const barWidth = `${pctValue}%`;

              return (
                <div key={stat.key} className="flex items-center gap-3">
                  <span className="font-medium w-44">{stat.label}</span>
                  <div className="relative flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getBarColorClass(pctValue)}`}
                      style={{ width: barWidth }}
                    />
                  </div>
                  <span className="min-w-[3.5rem] text-right">{formatStatValue(value, stat.key)}</span>
                  <span className={`${getColorClass(pctValue)} font-bold`}>{formatPercentile(pct)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}




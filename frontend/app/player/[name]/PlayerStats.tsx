"use client";

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
  const decimalPercentKeys = new Set(["ts_pct", "usg_pct", "efg_pct"]);

  const formatStatValue = (value: number, key: string) => {
    if (!Number.isFinite(value)) return "N/A";
    if (decimalPercentKeys.has(key)) {
      return `${(value * 100).toFixed(1)}%`;
    }
    return value.toFixed(1);
  };

  // Helper for the progress bar background color
  const getBarColorClass = (pct: number) => {
    if (pct >= 80) return "bg-red-500";
    if (pct <= 20) return "bg-blue-500";
    return "bg-gray-500";
  };

  // Reordered stats so points, assists, and rebounds appear first
  const statsConfig = [
    { label: "Points per 36", key: "pts", pctKey: "pts_pct" },
    { label: "Assists per 36", key: "ast", pctKey: "ast_pct" },
    { label: "Rebounds per 36", key: "reb", pctKey: "reb_pct" },
    { label: "Offensive Rating", key: "off_rating", pctKey: "off_rating_pct" },
    { label: "Defensive Rating", key: "def_rating", pctKey: "def_rating_pct" },
    { label: "True Shooting %", key: "ts_pct", pctKey: "ts_pct_pct" },
    { label: "Usage %", key: "usg_pct", pctKey: "usg_pct_pct" },
    { label: "Effective FG %", key: "efg_pct", pctKey: "efg_pct_pct" },
    { label: "PIE", key: "pie", pctKey: "pie_pct" },
  ];

  return (
    <section className="flex-1 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4">Stats & Percentiles</h2>
      <div className="space-y-4">
        {statsConfig.map((stat) => {
          const value = playerStats[stat.key];
          const pct = playerPercentiles[stat.pctKey]; // 0-100
          const barWidth = `${pct}%`;

          return (
            <div key={stat.key} className="flex items-center gap-3">
              {/* Stat Label */}
              <span className="font-medium w-40">{stat.label}</span>

              {/* Progress Bar */}
              <div className="relative flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColorClass(pct)}`}
                  style={{ width: barWidth }}
                />
              </div>

              {/* Stat Value & Percentile */}
              <span className="min-w-[3rem] text-right">{formatStatValue(value, stat.key)}</span>
              <span className={`${getColorClass(pct)} font-bold`}>
                {Math.round(pct)}%
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}




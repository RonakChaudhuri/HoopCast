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
  const statsConfig = [
    { label: "Offensive Rating", key: "off_rating", pctKey: "off_rating_pct" },
    { label: "Defensive Rating", key: "def_rating", pctKey: "def_rating_pct" },
    { label: "True Shooting %", key: "ts_pct", pctKey: "ts_pct_pct" },
    { label: "Usage %", key: "usg_pct", pctKey: "usg_pct_pct" },
    { label: "Effective FG %", key: "efg_pct", pctKey: "efg_pct_pct" },
    { label: "PIE", key: "pie", pctKey: "pie_pct" },
    { label: "Points per 36", key: "pts", pctKey: "pts_pct" },
    { label: "Rebounds per 36", key: "reb", pctKey: "reb_pct" },
    { label: "Assists per 36", key: "ast", pctKey: "ast_pct" },
  ];

  return (
    <section className="flex-1 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4">Stats & Percentiles</h2>
      <div className="space-y-4">
        {statsConfig.map((stat) => {
          const value = playerStats[stat.key];
          const pct = playerPercentiles[stat.pctKey];
          return (
            <div key={stat.key} className="flex justify-between items-center">
              <span className="font-medium">{stat.label}</span>
              <div className="flex items-center gap-2">
                <span>{value}</span>
                <span className={`${getColorClass(pct)} font-bold`}>
                  {Math.round(pct)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

"use client";

interface TraditionalStats {
  ppg: number;
  apg: number;
  rpg: number;
  spg: number;
  bpg: number;
  fg_pct: number;
  fg3_pct: number;
  ft_pct: number;
}

interface PlayerInfoProps {
  playerInfo: {
    full_name: string;
    team: string;
    position: string;
    birthdate: string;
    height: string | number;
    weight: string | number;
  };
  traditionalStats?: TraditionalStats; // optional prop
}

export default function PlayerInfo({ playerInfo, traditionalStats }: PlayerInfoProps) {
  return (
    <section className="flex-1 bg-white dark:bg-gray-800 p-8 rounded-lg shadow flex flex-col items-center text-center">
      {/* Player Name at top, underlined */}
      <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6 underline">
        {playerInfo.full_name}
      </h2>

      {/* Basic Player Details */}
      <div className="text-xl space-y-3 text-gray-800 dark:text-gray-100">
        <p><strong>Team:</strong> {playerInfo.team}</p>
        <p><strong>Position:</strong> {playerInfo.position}</p>
        <p><strong>Birthdate:</strong> {playerInfo.birthdate}</p>
        <p><strong>Height:</strong> {playerInfo.height}</p>
        <p><strong>Weight:</strong> {playerInfo.weight}</p>
      </div>

      {traditionalStats && (
        <div className="w-full mt-8">
          <table className="w-full text-center border-collapse">
            <thead>
              <tr className="bg-gray-100 dark:bg-gray-700 text-sm sm:text-base">
                <th className="p-2">PPG</th>
                <th className="p-2">APG</th>
                <th className="p-2">RPG</th>
                <th className="p-2">SPG</th>
                <th className="p-2">BPG</th>
                <th className="p-2">FG%</th>
                <th className="p-2">3PT%</th>
                <th className="p-2">FT%</th>
              </tr>
            </thead>
            <tbody>
              <tr className="text-sm sm:text-base">
                <td className="p-2">{traditionalStats.ppg}</td>
                <td className="p-2">{traditionalStats.apg}</td>
                <td className="p-2">{traditionalStats.rpg}</td>
                <td className="p-2">{traditionalStats.spg}</td>
                <td className="p-2">{traditionalStats.bpg}</td>
                <td className="p-2">{traditionalStats.fg_pct}%</td>
                <td className="p-2">{traditionalStats.fg3_pct}%</td>
                <td className="p-2">{traditionalStats.ft_pct}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

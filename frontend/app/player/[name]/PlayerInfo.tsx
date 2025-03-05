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
    birthdate: string;       // "YYYY-MM-DD"
    height: number | string; // total inches
    weight: number | string;
  };
  traditionalStats?: TraditionalStats;
}

/** 
 * Convert "YYYY-MM-DD" birthdate into an integer age. 
 */
function getAgeFromBirthdate(birthdate: string): number | null {
  if (!birthdate) return null;
  try {
    // Parse the birthdate (YYYY-MM-DD) into a Date object
    const [year, month, day] = birthdate.split("-").map(Number);
    const bday = new Date(year, month - 1, day);
    if (isNaN(bday.getTime())) return null; // invalid date

    const now = new Date();
    let age = now.getFullYear() - bday.getFullYear();

    // If the current date is before the birthdate in the current year, subtract 1
    const monthDiff = now.getMonth() - bday.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < bday.getDate())) {
      age--;
    }
    return age;
  } catch (e) {
    console.error("Error calculating age:", e);
    return null;
  }
}

/**
 * Convert total inches (e.g., 81) into feet/inches (e.g., "6'9\"").
 */
function convertInchesToFeetAndInches(value: number): string {
  if (!value || value <= 0) return "";
  const feet = Math.floor(value / 12);
  const inches = value % 12;
  return `${feet}'${inches}"`;
}

export default function PlayerInfo({ playerInfo, traditionalStats }: PlayerInfoProps) {
  // Calculate age from birthdate
  const age = getAgeFromBirthdate(playerInfo.birthdate);

  // Convert height to ft/in if it's a number
  let heightDisplay = "";
  if (typeof playerInfo.height === "number") {
    heightDisplay = convertInchesToFeetAndInches(playerInfo.height);
  } else {
    // If it's a string, parse it first
    const numericHeight = parseInt(playerInfo.height, 10);
    heightDisplay = convertInchesToFeetAndInches(numericHeight);
  }

  return (
    <section className="flex-1 bg-white dark:bg-gray-800 p-8 rounded-lg shadow flex flex-col items-center text-center">
      {/* Player Name */}
      <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6 underline">
        {playerInfo.full_name}
      </h2>

      {/* Basic Player Details */}
      <div className="text-xl space-y-3 text-gray-800 dark:text-gray-100">
        <p>
          <strong>Team:</strong> {playerInfo.team}
        </p>
        <p>
          <strong>Position:</strong> {playerInfo.position}
        </p>
        {age !== null ? (
          <p>
            <strong>Age:</strong> {age}
          </p>
        ) : (
          <p>
            <strong>Age:</strong> N/A
          </p>
        )}
        <p>
          <strong>Height:</strong> {heightDisplay}
        </p>
        <p>
          <strong>Weight:</strong> {playerInfo.weight}
        </p>
      </div>

      {/* Horizontal Box for Traditional Stats */}
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

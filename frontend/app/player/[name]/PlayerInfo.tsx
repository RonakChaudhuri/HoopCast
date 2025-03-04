"use client";

interface PlayerInfoProps {
  playerInfo: {
    full_name: string;
    team: string;
    position: string;
    birthdate: string;
    height: string | number;
    weight: string | number;
  };
}

export default function PlayerInfo({ playerInfo }: PlayerInfoProps) {
  return (
    <section className="flex-1 bg-white dark:bg-gray-800 p-8 rounded-lg shadow flex flex-col items-center text-center">
      {/* Player Name at top, underlined */}
      <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6 underline">
        {playerInfo.full_name}
      </h2>

      {/* Player details in larger text, centered */}
      <div className="text-xl space-y-3 text-gray-800 dark:text-gray-100">
        <p>
          <strong>Team:</strong> {playerInfo.team}
        </p>
        <p>
          <strong>Position:</strong> {playerInfo.position}
        </p>
        <p>
          <strong>Birthdate:</strong> {playerInfo.birthdate}
        </p>
        <p>
          <strong>Height:</strong> {playerInfo.height}
        </p>
        <p>
          <strong>Weight:</strong> {playerInfo.weight}
        </p>
      </div>
    </section>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import SearchBar from "@/app/components/SearchBar";
import PlayerInfo from "./PlayerInfo";
import PlayerStats from "./PlayerStats";
import PlayerNotFound from "@/app/components/PlayerNotFound";

export default function PlayerPage() {
  const { name } = useParams(); // dynamic route parameter
  const router = useRouter();

  const [playerInfo, setPlayerInfo] = useState<any>(null);
  const [playerStats, setPlayerStats] = useState<any>(null);
  const [playerPercentiles, setPlayerPercentiles] = useState<any>(null);
  const [traditionalStats, setTraditionalStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!name) return;

    const playerName = Array.isArray(name) ? name[0] : name;
    const decodedName = decodeURIComponent(playerName).trim();
    const finalName = encodeURIComponent(decodedName);
    console.log("Searching for player:", decodedName);

    Promise.all([
      fetch(`http://127.0.0.1:8000/players/by-name/${finalName}`).then(
        (res) => (res.ok ? res.json() : Promise.reject("Player not found"))
      ),
      fetch(`http://127.0.0.1:8000/stats/by-name/${finalName}`).then(
        (res) => (res.ok ? res.json() : Promise.reject("Stats not found"))
      ),
      fetch(`http://127.0.0.1:8000/stats/percentiles/by-name/${finalName}`).then(
        (res) => (res.ok ? res.json() : Promise.reject("Percentiles not found"))
      ),
      fetch(`http://127.0.0.1:8000/traditional_stats/by-name/${finalName}`).then(
        (res) => (res.ok ? res.json() : Promise.reject("Traditional stats not found"))
      ),
    ])
      .then(([infoData, statsData, percentilesData, traditionalData]) => {
        setPlayerInfo(infoData);
        setPlayerStats(statsData);
        setPlayerPercentiles(percentilesData);
        setTraditionalStats(traditionalData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        const errMsg = err instanceof Error ? err.message : String(err);
        if (errMsg === "Player not found") {
          setNotFound(true);
        } else {
          setError(errMsg);
        }
        setLoading(false);
      });
  }, [name]);

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  // Always render the header
  const header = (
    <header className="p-4 border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-100">
          HoopCast
        </h1>
        <SearchBar placeholder="Search player..." />
      </div>
    </header>
  );

  if (notFound) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {header}
        <main className="container mx-auto p-4">
          <PlayerNotFound />
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {header}
        <main className="container mx-auto p-4">
          <div className="text-center text-2xl text-red-500">Error: {error}</div>
        </main>
      </div>
    );
  }

  const getColorClass = (pct: number) => {
    if (pct >= 80) return "text-red-500";
    if (pct <= 20) return "text-blue-500";
    return "text-gray-500";
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {header}
      <main className="container mx-auto p-4 flex flex-col md:flex-row gap-8">
        <PlayerInfo playerInfo={playerInfo} traditionalStats={traditionalStats} />
        <PlayerStats
          playerStats={playerStats}
          playerPercentiles={playerPercentiles}
          getColorClass={getColorClass}
        />
      </main>
    </div>
  );
}

"use client";

export default function PlayerNotFound() {
  return (
    <div className="container mx-auto p-4 text-center">
      <h2 className="text-3xl font-bold text-red-500 mb-4">Player not found.</h2>
      <p className="text-xl">Please try searching for another player.</p>
    </div>
  );
}

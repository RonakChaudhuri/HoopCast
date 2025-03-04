"use client";

import SearchBar from "@/app/components/SearchBar";

export default function Home() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-800 dark:text-gray-100 mb-12">
          HoopCast
        </h1>
        <SearchBar placeholder="Search Player Name..." />
      </div>
    </div>
  );
}

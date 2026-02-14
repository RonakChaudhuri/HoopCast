"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

interface SearchBarProps {
  placeholder?: string;
  initialValue?: string;
}

interface PlayerSuggestion {
  player_id: number;
  full_name: string;
  team?: string | null;
}

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export default function SearchBar({ placeholder = "Search player...", initialValue = "" }: SearchBarProps) {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState<PlayerSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement | null>(null);

  const handleSearch = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      setShowSuggestions(false);
      router.push(`/player/${encodeURIComponent(trimmed)}`);
    }
  };

  const handleSelectSuggestion = (fullName: string) => {
    setQuery(fullName);
    setSuggestions([]);
    setShowSuggestions(false);
    router.push(`/player/${encodeURIComponent(fullName)}`);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setSuggestions([]);
      return;
    }

    const controller = new AbortController();
    const timeout = setTimeout(async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/players/search?q=${encodeURIComponent(trimmed)}&limit=8`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          setSuggestions([]);
          return;
        }

        const data: PlayerSuggestion[] = await response.json();
        setSuggestions(data);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
      }
    }, 200);

    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, [query]);

  return (
    <form onSubmit={handleSearch} className="flex justify-center">
      <div ref={containerRef} className="relative w-full max-w-5xl">
        <input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => {
            if (suggestions.length > 0) {
              setShowSuggestions(true);
            }
          }}
          className="w-full border border-gray-300 rounded-full py-5 px-6 text-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          title="Search"
          className="absolute right-0 top-0 h-full flex items-center justify-center pr-6"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-8 h-8 text-gray-400 hover:text-gray-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-4.35-4.35M9 17a8 8 0 100-16 8 8 0 000 16z"
            />
          </svg>
        </button>

        {showSuggestions && suggestions.length > 0 && (
          <ul className="absolute z-20 mt-2 w-full rounded-2xl border border-gray-200 bg-white shadow-lg overflow-hidden">
            {suggestions.map((player) => (
              <li key={player.player_id}>
                <button
                  type="button"
                  onMouseDown={() => handleSelectSuggestion(player.full_name)}
                  className="w-full text-left px-5 py-3 hover:bg-gray-100 transition-colors"
                >
                  <span className="font-medium text-gray-900">{player.full_name}</span>
                  {player.team ? <span className="ml-2 text-sm text-gray-500">({player.team})</span> : null}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </form>
  );
}


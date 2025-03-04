# HoopCast

HoopCast is an NBA statcast-style web application that displays advanced statistics and percentile rankings for NBA players. It provides detailed per-36-minute and advanced metrics for current season players, allowing users to search for a player and view their advanced stats in an interactive, visually appealing interface. Similar to baseball savants statcast, you can view players percentile in each advanced stat.

## Features

- **Player Search:**  
  Easily search for any active NBA player by name.
- **Advanced & Traditional Stats:**  
  View per-36-minute stats (points, rebounds, assists) along with advanced metrics such as Offensive Rating, Defensive Rating, True Shooting Percentage, Usage Percentage, Effective FG Percentage, PIE, etc.
- **Percentile Rankings:**  
  Compare player performance with percentile rankings displayed with color-coded visual cues (red for top performers, blue for lower performers).
- **Modern, Minimalist UI:**  
  A responsive design built with Next.js and Tailwind CSS that mirrors the simplicity of a search engine interface.

## Tech Stack

- **Frontend:**
  - Next.js (App Router)
  - React
  - Tailwind CSS
- **Backend:**
  - FastAPI
  - Python
  - nba_api (to fetch NBA statistics)
- **Database:**
  - PostgreSQL
- **Version Control:**
  - Git and GitHub

## Installation & Setup

### Prerequisites

- **Node.js** (v18+ recommended)
- **Python** (v3.9+ recommended)
- **PostgreSQL** (v12+ recommended)
- **Git**

### Backend Setup

1. **Navigate to the backend directory:**

   ```bash
   cd HoopCast/backend

   ```

2. **Create a virtual environment and activate it:**

   ```python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate

   ```

3. **Install Python dependencies:**

   ```pip install fastapi uvicorn psycopg2-binary nba_api python-dotenv

   ```

4. **Set up environment variables:**

   ```DATABASE=hoopcast
    USER=your_db_user
    PASSWORD=your_db_password
    HOST=localhost
    PORT=5432

   ```

5. **Set up environment variables:**

   ```DATABASE=hoopcast
    USER=your_db_user
    PASSWORD=your_db_password
    HOST=localhost
    PORT=5432

   ```

6. **Test the backend:**

   Visit http://127.0.0.1:8000/docs to view and test your API endpoints.

### Frontend Setup

1. **Navigate to the app (frontend) directory::**

   ```cd HoopCast/app

   ```

2. **Install Node.js dependencies:**

   ```npm install

   ```

3. **Run the Next.js development server:**

   ```npm run dev

   ```

4. **Access the frontend:**

   Open http://localhost:3000 in your browser to see the HoopCast homepage.

## Usage

### Homepage

- The homepage features a large, centered search bar with the "HoopCast" title.
- Type a player’s name (e.g., "LeBron James") into the search bar and hit enter to view the player's detail page.

### Player Detail Page

- The player detail page displays:
  - **Basic Player Information:** Name, team, position, birthdate, height, and weight.
  - **Stats & Percentiles:** Advanced and traditional stats with color-coded percentiles to indicate how the player ranks in each category.
- A search bar at the top of the page allows you to quickly search for another player.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License.

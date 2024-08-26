import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import "./App.css";
import RecordPage from "./RecordPage";
import PlaybackPage from "./playback";

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Siren Dashboard</h1>
          <nav>
            <ul>
              <li>
                <Link to="./RecordPage">Record</Link>
              </li>
              <li>
                <Link to="/playback">Playback</Link>
              </li>
            </ul>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/RecordPage" element={<RecordPage />} />
            <Route path="/playback" element={<PlaybackPage />} />
            <Route
              path="/" //landing page
              element={
                <div>
                  <h2>Siren Dashboard</h2>
                </div>
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

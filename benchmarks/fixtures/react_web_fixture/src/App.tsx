import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

const Home = React.lazy(() => import('./components/Home'));
const Profile = React.lazy(() => import('./components/Profile'));
const Settings = React.lazy(() => import('./components/Settings'));

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/profile">Profile</Link>
        <Link to="/settings">Settings</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/profile/:id" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/about" element={<div>About</div>} />
      </Routes>
    </BrowserRouter>
  );
}

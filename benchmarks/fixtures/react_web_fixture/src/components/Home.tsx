import React from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL;

export default function Home() {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/profile/123");
  };

  return <div onClick={handleClick}>Home</div>;
}

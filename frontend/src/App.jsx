import React, { useState } from 'react';
import Welcome from './components/Welcome';
import Login from './components/Login';
import Registration from './components/Registration';
import Home from './components/Home';
import './App.css';

function App() {
  const [screen, setScreen] = useState('welcome');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setScreen('home');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setScreen('welcome');
  };

  return (
    <div className="app">
      {screen === 'welcome' ? (
        <Welcome
          onLoginClick={() => setScreen('login')}
          onRegisterClick={() => setScreen('registration')}
        />
      ) : screen === 'login' ? (
        <Login onBackClick={() => setScreen('welcome')} onLoginSuccess={handleLoginSuccess} />
      ) : screen === 'registration' ? (
        <Registration onBackClick={() => setScreen('welcome')} />
      ) : screen === 'home' && isAuthenticated ? (
        <Home onLogout={handleLogout} />
      ) : null}
    </div>
  );
}

export default App;
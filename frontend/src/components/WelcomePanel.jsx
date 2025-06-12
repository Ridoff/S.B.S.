import React from 'react';
import 'frontend/src/components/WelcomePanel.css';
import logo from 'frontend/src/assets/seatly_logo.png';

const Welcome = ({ onLoginClick, onRegisterClick }) => {
  return (
    <div className="welcome-container">
      <img src={logo} alt="Seatly Logo" className="welcome-logo" />
      <h1 className="welcome-title">WELCOME • • •</h1>
      <button className="welcome-button" onClick={onLoginClick}>
        log in
      </button>
      <button className="welcome-button" onClick={onRegisterClick}>
        register
      </button>
      <p className="welcome-copyright">© SEATLY CORP 2025</p>
    </div>
  );
};

export default Welcome;
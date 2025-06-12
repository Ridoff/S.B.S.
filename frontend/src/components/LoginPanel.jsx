import React, { useState } from 'react';
import 'frontend/src/components/LoginPanel.css';
import axios from 'axios';

const Login = ({ onBackClick, onLoginSuccess }) => {
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/auth/login', formData);
      alert('Вход успешен!');
      onLoginSuccess();
    } catch (error) {
      alert('Ошибка входа: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="login-container">
      <img src="/logo.png" alt="Seatly Logo" className="login-logo" />
      <h1 className="login-title">LOG IN • • •</h1>
      <form className="login-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          className="login-input"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          className="login-input"
        />
        <button type="submit" className="login-button">
          log in
        </button>
      </form>
      <button className="login-back" onClick={onBackClick}>
        Back
      </button>
      <p className="login-copyright">© SEATLY CORP 2025</p>
    </div>
  );
};

export default Login;
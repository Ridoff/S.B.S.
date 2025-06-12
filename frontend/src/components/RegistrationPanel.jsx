import React, { useState } from 'react';
import 'frontend/src/components/RegistrationPanel.css';
import axios from 'axios';

const Registration = ({ onBackClick }) => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/auth/register', formData);
      alert('Регистрация успешна! Теперь войдите.');
      onBackClick();
    } catch (error) {
      alert('Ошибка регистрации: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="registration-container">
      <img src="/logo.png" alt="Seatly Logo" className="registration-logo" />
      <h1 className="registration-title">REGISTER • • •</h1>
      <form className="registration-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          className="registration-input"
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className="registration-input"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          className="registration-input"
        />
        <button type="submit" className="registration-button">
          register
        </button>
      </form>
      <button className="registration-back" onClick={onBackClick}>
        Back
      </button>
      <p className="registration-copyright">© SEATLY CORP 2025</p>
    </div>
  );
};

export default Registration;
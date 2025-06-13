import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  test('renders Welcome screen by default', () => {
    render(<App />);
    expect(screen.getByText(/Welcome to Seatly/i)).toBeInTheDocument();
  });

  test('switches to Login screen on Login click', () => {
    render(<App />);
    fireEvent.click(screen.getByText(/Log In/i));
    expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
  });

  test('switches to Registration screen on Register click', () => {
    render(<App />);
    fireEvent.click(screen.getByText(/Register/i));
    expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
  });

  test('switches to Home after successful login', () => {
    render(<App />);
    fireEvent.click(screen.getByText(/Log In/i));
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'test' } });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'test' } });
    fireEvent.click(screen.getByText(/log in/i));
    expect(screen.getByText(/Top restaurants this week/i)).toBeInTheDocument();
  });

  test('handles login failure gracefully', () => {
    render(<App />);
    fireEvent.click(screen.getByText(/Log In/i));
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'wrong' } });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByText(/log in/i));
    expect(screen.queryByText(/Top restaurants this week/i)).not.toBeInTheDocument();
    expect(screen.getByText(/LOG IN/i)).toBeInTheDocument();
  });
});
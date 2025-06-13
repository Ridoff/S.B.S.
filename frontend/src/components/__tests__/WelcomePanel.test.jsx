import { render, screen, fireEvent } from '@testing-library/react';
import Welcome from '../Welcome';

describe('Welcome Component', () => {
  test('renders welcome message', () => {
    render(<Welcome onLoginClick={jest.fn()} onRegisterClick={jest.fn()} />);
    expect(screen.getByText(/Welcome to Seatly/i)).toBeInTheDocument();
  });

  test('calls onLoginClick on Log In click', () => {
    const mockLogin = jest.fn();
    render(<Welcome onLoginClick={mockLogin} onRegisterClick={jest.fn()} />);
    fireEvent.click(screen.getByText(/Log In/i));
    expect(mockLogin).toHaveBeenCalledTimes(1);
  });

  test('calls onRegisterClick on Register click', () => {
    const mockRegister = jest.fn();
    render(<Welcome onLoginClick={jest.fn()} onRegisterClick={mockRegister} />);
    fireEvent.click(screen.getByText(/Register/i));
    expect(mockRegister).toHaveBeenCalledTimes(1);
  });
});
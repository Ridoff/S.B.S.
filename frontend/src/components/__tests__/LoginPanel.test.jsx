import { render, screen, fireEvent } from '@testing-library/react';
import Login from '../Login';

describe('Login Component', () => {
  const mockBack = jest.fn();
  const mockLoginSuccess = jest.fn();

  beforeEach(() => {
    render(<Login onBackClick={mockBack} onLoginSuccess={mockLoginSuccess} />);
  });

  test('renders login form', () => {
    expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
    expect(screen.getByText(/log in/i)).toBeInTheDocument();
  });

  test('submits form with valid data', () => {
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'test' } });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'test' } });
    fireEvent.click(screen.getByText(/log in/i));
    expect(mockLoginSuccess).toHaveBeenCalledTimes(1);
  });

  test('does not submit with empty fields', () => {
    fireEvent.click(screen.getByText(/log in/i));
    expect(mockLoginSuccess).not.toHaveBeenCalled();
  });

  test('calls back on Back click', () => {
    fireEvent.click(screen.getByText(/Back/i));
    expect(mockBack).toHaveBeenCalledTimes(1);
  });

  test('renders logo', () => {
    const logo = screen.getByAltText(/Seatly Logo/i);
    expect(logo).toBeInTheDocument();
    expect(logo.src).toContain('logo.png');
  });
});
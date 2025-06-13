import { render, screen, fireEvent } from '@testing-library/react';
import Registration from '../Registration';

describe('Registration Component', () => {
  const mockBack = jest.fn();

  beforeEach(() => {
    render(<Registration onBackClick={mockBack} />);
  });

  test('renders registration form', () => {
    expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
    expect(screen.getByText(/Register/i)).toBeInTheDocument();
  });

  test('does not submit with empty fields', () => {
    fireEvent.click(screen.getByText(/Register/i));
    expect(screen.getByText(/Register/i)).toBeInTheDocument();
  });

  test('calls back on Back click', () => {
    fireEvent.click(screen.getByText(/Back/i));
    expect(mockBack).toHaveBeenCalledTimes(1);
  });
});
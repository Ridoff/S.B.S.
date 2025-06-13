import { render, screen, fireEvent } from '@testing-library/react';
import Home from '../Home';
import { MemoryRouter } from 'react-router-dom';

describe('Home Component', () => {
  const mockLogout = jest.fn();

  beforeEach(() => {
    render(
      <MemoryRouter>
        <Home onLogout={mockLogout} />
      </MemoryRouter>
    );
  });

  test('renders search bar', () => {
    const searchBar = screen.getByPlaceholderText(/search/i);
    expect(searchBar).toBeInTheDocument();
    expect(searchBar.value).toBe('');
  });

  test('updates search input value', () => {
    const searchBar = screen.getByPlaceholderText(/search/i);
    fireEvent.change(searchBar, { target: { value: 'test' } });
    expect(searchBar.value).toBe('test');
  });

  test('renders restaurant placeholders', () => {
    const restaurantNames = screen.getAllByText(/Le Restaurant/i);
    expect(restaurantNames.length).toBe(2);
  });

  test('calls onLogout when button is clicked', () => {
    const logoutButton = screen.getByText(/Logout/i);
    fireEvent.click(logoutButton);
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  test('handles empty search gracefully', () => {
    const searchBar = screen.getByPlaceholderText(/search/i);
    fireEvent.change(searchBar, { target: { value: '' } });
    expect(screen.getAllByText(/Le Restaurant/i).length).toBe(2);
  });

  test('renders profile placeholder', () => {
    const profileIcon = screen.getByAltText(/Profile Placeholder/i);
    expect(profileIcon).toBeInTheDocument();
    expect(profileIcon.src).toContain('profile-placeholder.png');
  });
});
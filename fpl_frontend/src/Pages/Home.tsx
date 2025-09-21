import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import '../styles/Global.css';
import '../Components/Navbar/Navbar.css';
import '../styles/Home.css';
import '../styles/SignIn.css';
import Button from '../Components/Button/Button';

interface Suggestion {
  type: 'team' | 'name' | 'both';
  team_name: string;
  full_name: string;
  display: string;
}

function App() {
  const signInRef = useRef<HTMLDivElement>(null);
  const landingRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  // Autocomplete state
  const [teamSuggestions, setTeamSuggestions] = useState<Suggestion[]>([]);
  const [nameSuggestions, setNameSuggestions] = useState<Suggestion[]>([]);
  const [showTeamSuggestions, setShowTeamSuggestions] = useState(false);
  const [showNameSuggestions, setShowNameSuggestions] = useState(false);
  const [teamName, setTeamName] = useState('');
  const [fullName, setFullName] = useState('');

  // Smooth scroll to sign-in
  const scrollToSignIn = () => {
    signInRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Fetch autocomplete suggestions
  const fetchSuggestions = async (query: string, field: 'team' | 'name') => {
    if (query.length < 2) {
      if (field === 'team') {
        setTeamSuggestions([]);
        setShowTeamSuggestions(false);
      } else {
        setNameSuggestions([]);
        setShowNameSuggestions(false);
      }
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/autocomplete/?q=${encodeURIComponent(query)}&field=${field}`);
      if (response.ok) {
        const data = await response.json();
        const suggestions = data.suggestions.filter((s: Suggestion) => s.type === field);
        
        if (field === 'team') {
          setTeamSuggestions(suggestions);
          setShowTeamSuggestions(suggestions.length > 0);
        } else {
          setNameSuggestions(suggestions);
          setShowNameSuggestions(suggestions.length > 0);
        }
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  // Handle team name input change
  const handleTeamNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTeamName(value);
    fetchSuggestions(value, 'team');
  };

  // Handle full name input change
  const handleFullNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFullName(value);
    fetchSuggestions(value, 'name');
  };

  // Handle suggestion selection - now populates both fields
  const handleSuggestionSelect = (suggestion: Suggestion) => {
    setTeamName(suggestion.team_name);
    setFullName(suggestion.full_name);
    setShowTeamSuggestions(false);
    setShowNameSuggestions(false);
  };

// Navigate to Connect page and connect to backend API
const handleConnect = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!teamName || !fullName) {
    alert('Please fill in both team name and full name');
    return;
  }

  // Fetch from API
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/get_player_id/?playerName=${encodeURIComponent(fullName)}&teamName=${encodeURIComponent(teamName)}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get player ID');
    }
    
    const data = await response.json();
    console.log("Received from Django:", data);

    if (data.player_id) {
      // Store the player ID and other data for the Connect page
      localStorage.setItem('playerId', data.player_id);
      localStorage.setItem('playerName', fullName);
      localStorage.setItem('teamName', teamName);
      
      // Navigate to the connect page
      navigate('/connect');
    } else {
      throw new Error('Player ID not found');
    }
  } catch (err) {
    console.error("API error:", err);
    alert(err instanceof Error ? err.message : 'Failed to connect. Please check your team name and full name.');
  }
};

  return (
    <>
      {/* NAVBAR (fixed at top) */}
      <nav className="navbar">
        <div className="navbar-logo">FPL Pulse</div>
        <div className="navbar-links">
          <Link to='/'>Home</Link>
          <a onClick={scrollToSignIn}>Connect</a>
        </div>
      </nav>

      {/* HERO SECTION: full screen, out of the normal doc flow below the fixed nav */}
      <section ref={landingRef} className="hero-container">
        <div className="hero-content">
          <p className="hero-subtitle">It's almost time</p>
          <h1 className="hero-title">FPL Betting, Re‑Imagined!</h1>
          <Button 
            label="Get Started" 
            onClick={scrollToSignIn} 
            className="hero-button" 
        />
        </div>
      </section>

      {/* SIGN-IN SECTION: also full screen, visually below hero */}
      <section ref={signInRef} className="sign-in-section">
        <h2>Connect your Fantasy Premier League team!</h2>
        <form onSubmit={handleConnect}>
          <div className="autocomplete-container">
            <label htmlFor="teamName">Team name *</label>
            <input
              id="teamName"
              type="text"
              placeholder="Enter your team name"
              value={teamName}
              onChange={handleTeamNameChange}
              onFocus={() => setShowTeamSuggestions(teamSuggestions.length > 0)}
              onBlur={() => setTimeout(() => setShowTeamSuggestions(false), 200)}
            />
            {showTeamSuggestions && teamSuggestions.length > 0 && (
              <div className="autocomplete-dropdown">
                {teamSuggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="autocomplete-item"
                    onClick={() => handleSuggestionSelect(suggestion)}
                  >
                    {suggestion.display}
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="autocomplete-container">
            <label htmlFor="fullName">Your full name *</label>
            <input
              id="fullName"
              type="text"
              placeholder="Enter your full name"
              value={fullName}
              onChange={handleFullNameChange}
              onFocus={() => setShowNameSuggestions(nameSuggestions.length > 0)}
              onBlur={() => setTimeout(() => setShowNameSuggestions(false), 200)}
            />
            {showNameSuggestions && nameSuggestions.length > 0 && (
              <div className="autocomplete-dropdown">
                {nameSuggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="autocomplete-item"
                    onClick={() => handleSuggestionSelect(suggestion)}
                  >
                    {suggestion.display}
                  </div>
                ))}
              </div>
            )}
          </div>
          <Button 
            label="Connect" 
            onClick={handleConnect} 
            type="submit" 
            className="connect-button" 
        />
        </form>
      </section>
    </>
  );
}

export default App;
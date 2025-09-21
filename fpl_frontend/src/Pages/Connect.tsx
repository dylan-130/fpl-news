import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../Components/Navbar/Navbar';
import '../styles/Global.css';
import '../Components/Navbar/Navbar.css';
import '../styles/Connect.css';
import PlayerCard from '../Components/PlayerCard/PlayerCard';
import Button from '../Components/Button/Button';

interface Player {
  id: number;
  name: string;
  points: number;
  position: number;
  element_type: number;
  is_captain: boolean;
  is_vice_captain: boolean;
  multiplier: number;
  team_name?: string;
}

const Connect = () => {
  const navigate = useNavigate();
  const [teamData, setTeamData] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gameweek, setGameweek] = useState(0);
  const [totalPoints, setTotalPoints] = useState(0);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        const playerId = localStorage.getItem('playerId');
        if (!playerId) {
          throw new Error('Player ID not found. Please try connecting again.');
        }

        // Fetch team data from the API
        const response = await fetch(`http://127.0.0.1:8000/api/async_get_team_data/?playerId=${playerId}`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to fetch team data');
        }
        
        const data = await response.json();
        console.log("Team data received:", data);
        
        if (data.team_data && Array.isArray(data.team_data)) {
          setTeamData(data.team_data);
          setGameweek(data.gameweek || 0);
          setTotalPoints(data.total_points || 0);
        } else {
          throw new Error('Invalid team data format');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load team');
        console.error("Error fetching team data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamData();
  }, []);

  // Total points are now calculated correctly in the backend
  // (excluding bench players unless bench boost is active)

  // Organize players by position
  const startingPlayers = teamData.filter(player => player.position <= 11);
  const benchPlayers = teamData.filter(player => player.position > 11);

  const positionGroups = {
    goalkeeper: startingPlayers.filter(p => p.element_type === 1),
    defenders: startingPlayers.filter(p => p.element_type === 2),
    midfielders: startingPlayers.filter(p => p.element_type === 3),
    forwards: startingPlayers.filter(p => p.element_type === 4)
  };

  if (loading) return <div className="loading">Loading team...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="page-container">
      <Navbar />
      
      <div className="connect-page">
        
        {/* Team Info */}
        <div className="team-info">
          <div className="team-name">{localStorage.getItem('teamName') || 'Team Name'}</div>
          <div className="team-manager">{localStorage.getItem('playerName') || 'Manager'}</div>
          <div className="game-week">GW {gameweek}</div>
          <div className="points">Points: {totalPoints}</div>
        </div>

        {/* Goalkeeper */}
        <section className="goalkeeper">
          {positionGroups.goalkeeper.map(player => (
            <PlayerCard
              key={player.id}
              name={player.name}
              points={player.points}
              isCaptain={player.is_captain}
              isViceCaptain={player.is_vice_captain}
            />
          ))}
        </section>

        {/* Defenders */}
        <section className="defenders">
          {positionGroups.defenders.map(player => (
            <PlayerCard
              key={player.id}
              name={player.name}
              points={player.points}
              isCaptain={player.is_captain}
              isViceCaptain={player.is_vice_captain}
              showSubOff={player.multiplier === 0}
            />
          ))}
        </section>

        {/* Midfielders */}
        <section className="midfielders">
          {positionGroups.midfielders.map(player => (
            <PlayerCard
              key={player.id}
              name={player.name}
              points={player.points}
              isCaptain={player.is_captain}
              isViceCaptain={player.is_vice_captain}
              showSubOff={player.multiplier === 0}
            />
          ))}
        </section>

        {/* Forwards */}
        <section className="forwards">
          {positionGroups.forwards.map(player => (
            <PlayerCard
              key={player.id}
              name={player.name}
              points={player.points}
              isCaptain={player.is_captain}
              isViceCaptain={player.is_vice_captain}
              showSubOff={player.multiplier === 0}
            />
          ))}
        </section>

        {/* Bench */}
        <section className="bench">
          {benchPlayers.slice(0, 4).map(player => (
            <PlayerCard
              key={player.id}
              name={player.name}
              points={player.points}
              showSubOn={player.multiplier === 1}
            />
          ))}
        </section>

        {/* Buttons */}
        <div className="bottom-right-buttons">
          <Button 
            label="Confirm & Get Bet-Builder" 
            onClick={() => navigate('/bet-builder')} 
            className="confirm-button" 
          />
          <Button 
            label="That's not my team" 
            onClick={() => navigate('/')} 
            className="cancel-button" 
          />
        </div>
      </div>
    </div>
  );
};

export default Connect;
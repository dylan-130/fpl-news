import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../Components/Navbar/Navbar';
import '../styles/Global.css';
import '../Components/Navbar/Navbar.css';
import '../styles/BetBuilder.css';
import Button from '../Components/Button/Button';

interface BetLeg {
  id: string;
  player: string;
  team: string;
  betType: string;
  odds: number;
  stake: number;
  potentialWin: number;
}

interface BetSlip {
  legs: BetLeg[];
  totalOdds: number;
  totalStake: number;
  potentialWin: number;
  luckLevel: number;
}

const BetBuilder = () => {
  const navigate = useNavigate();
  const [betSlip, setBetSlip] = useState<BetSlip>({
    legs: [],
    totalOdds: 1,
    totalStake: 10,
    potentialWin: 10,
    luckLevel: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [teamData, setTeamData] = useState<any[]>([]);
  const [isReturningUser, setIsReturningUser] = useState(false);

  useEffect(() => {
    const fetchBetBuilder = async () => {
      try {
        const playerId = localStorage.getItem('playerId');
        if (!playerId) {
          throw new Error('Player ID not found. Please try connecting again.');
        }

        // First check if user has betting history
        const historyResponse = await fetch(`http://127.0.0.1:8000/api/user_history/?playerId=${playerId}`);
        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          setIsReturningUser(historyData.bet_count > 0);
        }

        // Fetch team data and generate bet suggestions
        const response = await fetch(`http://127.0.0.1:8000/api/generate_bet_suggestions/?playerId=${playerId}&luckLevel=0`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to generate bet suggestions');
        }
        
        const data = await response.json();
        console.log("Bet suggestions received:", data);
        
        setTeamData(data.team_data || []);
        setBetSlip(prev => ({
          ...prev,
          legs: data.bet_legs || [],
          totalOdds: data.total_odds || 1,
          luckLevel: data.luck_level || 0,
          potentialWin: (data.total_odds || 1) * prev.totalStake
        }));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load bet builder');
        console.error("Error fetching bet suggestions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchBetBuilder();
  }, []);

  const adjustLuckLevel = async (direction: 'lucky' | 'unlucky') => {
    try {
      const playerId = localStorage.getItem('playerId');
      const newLuckLevel = direction === 'lucky' ? betSlip.luckLevel + 1 : betSlip.luckLevel - 1;
      
      const response = await fetch(`http://127.0.0.1:8000/api/adjust_odds/?playerId=${playerId}&luckLevel=${newLuckLevel}`);
      
      if (!response.ok) {
        throw new Error('Failed to adjust odds');
      }
      
      const data = await response.json();
      
      setBetSlip(prev => ({
        ...prev,
        legs: data.bet_legs || prev.legs,
        totalOdds: data.total_odds || prev.totalOdds,
        luckLevel: newLuckLevel,
        potentialWin: (data.total_odds || prev.totalOdds) * prev.totalStake
      }));
    } catch (err) {
      console.error("Error adjusting odds:", err);
    }
  };

  const placeBet = async () => {
    try {
      const playerId = localStorage.getItem('playerId');
      
      const betData = {
        playerId,
        legs: betSlip.legs,
        totalOdds: betSlip.totalOdds,
        totalStake: betSlip.totalStake,
        potentialWin: betSlip.potentialWin,
        luckLevel: betSlip.luckLevel
      };

      const response = await fetch('http://127.0.0.1:8000/api/place_bet/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(betData)
      });

      if (!response.ok) {
        throw new Error('Failed to place bet');
      }

      const data = await response.json();
      navigate('/bet-receipt', { state: { betData: data } });
    } catch (err) {
      console.error("Error placing bet:", err);
      alert('Failed to place bet. Please try again.');
    }
  };

  const updateStake = (newStake: number) => {
    setBetSlip(prev => ({
      ...prev,
      totalStake: newStake,
      potentialWin: prev.totalOdds * newStake
    }));
  };

  if (loading) return <div className="loading">Generating your personalized bet...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="page-container">
      <Navbar />
      
      <div className="bet-builder-page">
        <div className="bet-builder-header">
          <h1>🎯 Bet Builder</h1>
          <p>AI-powered betting based on your FPL team</p>
        </div>

        <div className="bet-builder-content">
          {/* Luck Adjustment Controls */}
          <div className="luck-controls">
            <div className="luck-info">
              <span className="luck-label">Luck Level: {betSlip.luckLevel}</span>
              <span className="luck-description">
                {betSlip.luckLevel === 0 && (isReturningUser ? "Standard odds - Use buttons to adjust" : "New user - Start with low odds")}
                {betSlip.luckLevel > 0 && `Feeling lucky! +${betSlip.luckLevel} level(s)`}
                {betSlip.luckLevel < 0 && `Playing it safe - ${Math.abs(betSlip.luckLevel)} level(s)`}
              </span>
            </div>
            
            <div className="luck-buttons">
              <Button 
                label="🎰 I'm Feeling Lucky!" 
                onClick={() => adjustLuckLevel('lucky')}
                className="lucky-button"
              />
              {isReturningUser && (
                <Button 
                  label="😰 Not That Lucky" 
                  onClick={() => adjustLuckLevel('unlucky')}
                  className="unlucky-button"
                />
              )}
            </div>
          </div>

          {/* Bet Slip */}
          <div className="bet-slip">
            <div className="bet-slip-header">
              <h2>📋 Your Bet Slip</h2>
              <div className="odds-display">
                <span className="total-odds">Total Odds: {betSlip.totalOdds.toFixed(2)}</span>
              </div>
            </div>

            <div className="bet-legs">
              {betSlip.legs.map((leg, index) => (
                <div key={leg.id} className="bet-leg">
                  <div className="leg-info">
                    <div className="player-info">
                      <span className="player-name">{leg.player}</span>
                      <span className="team-name">{leg.team}</span>
                    </div>
                    <div className="bet-type">{leg.betType}</div>
                  </div>
                  <div className="leg-odds">
                    <span className="odds">{leg.odds.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="stake-section">
              <label htmlFor="stake">Stake (£):</label>
              <input
                id="stake"
                type="number"
                min="1"
                value={betSlip.totalStake}
                onChange={(e) => updateStake(Number(e.target.value))}
                className="stake-input"
              />
            </div>

            <div className="potential-win">
              <span className="win-label">Potential Win:</span>
              <span className="win-amount">£{betSlip.potentialWin.toFixed(2)}</span>
            </div>
          </div>

          {/* EMERGENCY BUTTON - GUARANTEED TO WORK */}
          <div style={{
            textAlign: 'center',
            padding: '20px',
            margin: '20px 0',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '15px',
            border: '2px solid rgba(255, 255, 255, 0.2)'
          }}>
            <button 
              onClick={placeBet}
              style={{
                background: 'linear-gradient(45deg, #4CAF50, #45a049)',
                color: 'white',
                fontWeight: 'bold',
                padding: '15px 30px',
                borderRadius: '25px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '16px',
                boxShadow: '0 4px 15px rgba(76, 175, 80, 0.3)',
                minWidth: '180px',
                transition: 'all 0.3s ease'
              }}
            >
              💰 Place Bet
            </button>
          </div>

          {/* Action Buttons */}
          <div className="bet-actions">
            <Button 
              label="🔙 Back to Team" 
              onClick={() => navigate('/connect')}
              className="back-button"
            />
            <Button 
              label="💰 Place Bet" 
              onClick={placeBet}
              className="place-bet-button"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default BetBuilder; 
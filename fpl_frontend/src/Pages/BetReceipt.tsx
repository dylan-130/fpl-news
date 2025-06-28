import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../Components/Navbar/Navbar';
import '../styles/Global.css';
import '../Components/Navbar/Navbar.css';
import '../styles/BetReceipt.css';
import Button from '../Components/Button/Button';

interface BetLeg {
  id: string;
  player: string;
  team: string;
  betType: string;
  odds: number;
}

interface BetReceiptData {
  betId: string;
  legs: BetLeg[];
  totalOdds: number;
  totalStake: number;
  potentialWin: number;
  luckLevel: number;
  timestamp: string;
}

const BetReceipt = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const betData: BetReceiptData = location.state?.betData;

  if (!betData) {
    return (
      <div className="page-container">
        <Navbar />
        <div className="error-container">
          <h2>No bet data found</h2>
          <p>Please place a bet to view the receipt.</p>
          <Button 
            label="Go to Bet Builder" 
            onClick={() => navigate('/bet-builder')}
            className="primary-button"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Navbar />
      
      <div className="bet-receipt-page">
        <div className="receipt-container">
          <div className="receipt-header">
            <div className="success-icon">✅</div>
            <h1>Bet Placed Successfully!</h1>
            <p>Thank you for your bet. Here's your receipt:</p>
          </div>

          <div className="receipt-details">
            <div className="receipt-section">
              <h3>📋 Bet Details</h3>
              <div className="detail-row">
                <span className="label">Bet ID:</span>
                <span className="value">{betData.betId}</span>
              </div>
              <div className="detail-row">
                <span className="label">Date:</span>
                <span className="value">{new Date(betData.timestamp).toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="label">Luck Level:</span>
                <span className="value">{betData.luckLevel}</span>
              </div>
            </div>

            <div className="receipt-section">
              <h3>🎯 Bet Legs</h3>
              <div className="bet-legs">
                {betData.legs.map((leg, index) => (
                  <div key={leg.id} className="receipt-leg">
                    <div className="leg-number">{index + 1}</div>
                    <div className="leg-details">
                      <div className="leg-player">{leg.player}</div>
                      <div className="leg-team">{leg.team}</div>
                      <div className="leg-type">{leg.betType}</div>
                    </div>
                    <div className="leg-odds">{leg.odds.toFixed(2)}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="receipt-section">
              <h3>💰 Bet Summary</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Total Odds:</span>
                  <span className="summary-value odds">{betData.totalOdds.toFixed(2)}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Stake:</span>
                  <span className="summary-value stake">£{betData.totalStake.toFixed(2)}</span>
                </div>
                <div className="summary-item highlight">
                  <span className="summary-label">Potential Win:</span>
                  <span className="summary-value win">£{betData.potentialWin.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="receipt-section">
              <h3>📱 Bet Status</h3>
              <div className="status-indicator">
                <div className="status-dot active"></div>
                <span className="status-text">Bet Confirmed - Awaiting Results</span>
              </div>
              <p className="status-note">
                Your bet has been successfully placed and is now active. 
                Results will be updated after the gameweek concludes.
              </p>
            </div>
          </div>

          <div className="receipt-actions">
            <Button 
              label="🏠 Go Home" 
              onClick={() => navigate('/')}
              className="home-button"
            />
            <Button 
              label="🎯 Place Another Bet" 
              onClick={() => navigate('/bet-builder')}
              className="another-bet-button"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default BetReceipt; 
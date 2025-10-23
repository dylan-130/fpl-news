import React from 'react';
import './ArticleDetail.css';

interface ArticleDetailProps {
  article: {
    headline: string;
    body: string;
    league_name: string;
    league_id: number;
    gameweek: number;
    position_change: number;
    current_position?: number;
    total_points?: number;
    league_standings?: any;
  };
  onClose: () => void;
}

const ArticleDetail: React.FC<ArticleDetailProps> = ({ article, onClose }) => {
  const renderArticleWithTable = () => {
    if (!article.body) return null;
    
    // Split the article body by the league table placeholder
    const parts = article.body.split('[LEAGUE_TABLE_PLACEHOLDER]');
    
    if (parts.length === 1) {
      // No placeholder found, render normally
      return (
        <div className="article-body-detail">
          <p>{article.body}</p>
        </div>
      );
    }
    
    // Render article with table in the middle
    return (
      <div className="article-body-detail">
        <p>{parts[0]}</p>
        
        {renderLeagueTable()}
        
        <p>{parts[1]}</p>
      </div>
    );
  };

  const getPositionArrow = (positionChange: number) => {
    if (positionChange > 0) return "↗";
    if (positionChange < 0) return "↘";
    return "→";
  };

  const renderLeagueTable = () => {
    if (!article.league_standings || !article.league_standings.standings) {
      return (
        <div className="league-table-placeholder">
          <p>League standings not available</p>
        </div>
      );
    }

    const standings = article.league_standings.standings.results;
    const positionChanges = article.all_position_changes || {};

    return (
      <div className="league-table-section">
        <h3>{article.league_name} Standings</h3>
        <div className="league-table">
          <div className="table-header">
            <div className="table-row header-row">
              <div className="col-position">Pos</div>
              <div className="col-team">Team</div>
              <div className="col-manager">Manager</div>
              <div className="col-points">Points</div>
              <div className="col-change">Change</div>
            </div>
          </div>
          <div className="table-body">
            {standings.slice(0, 10).map((entry: any, index: number) => {
              const positionChange = positionChanges[entry.entry] || 0;
              const arrow = getPositionArrow(positionChange);
              return (
                <div 
                  key={entry.entry} 
                  className={`table-row ${entry.entry === parseInt(localStorage.getItem('playerId') || '0') ? 'current-player' : ''}`}
                >
                  <div className="col-position">{index + 1}</div>
                  <div className="col-team">{entry.entry_name}</div>
                  <div className="col-manager">{entry.player_name}</div>
                  <div className="col-points">{entry.total}</div>
                  <div className="col-change">
                    {positionChange !== 0 && (
                      <span className={`position-change ${positionChange > 0 ? 'positive' : 'negative'}`}>
                        {arrow} {Math.abs(positionChange)}
                      </span>
                    )}
                    {positionChange === 0 && <span className="position-change neutral">{arrow}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="article-detail-overlay">
      <div className="article-detail-modal">
        <div className="article-detail-header">
          <h1>{article.headline}</h1>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>
        
        <div className="article-detail-content">
          <div className="article-meta">
            <span className="league-name">{article.league_name}</span>
            <span className="gameweek">
              Gameweek {article.gameweek}
              {article.position_change !== 0 && (
                <span className={`position-change-meta ${article.position_change > 0 ? 'positive' : 'negative'}`}>
                  {getPositionArrow(article.position_change)} {Math.abs(article.position_change)}
                </span>
              )}
              {article.position_change === 0 && (
                <span className="position-change-meta neutral">
                  {getPositionArrow(article.position_change)}
                </span>
              )}
            </span>
            {article.current_position && (
              <span className="current-position">
                Position: {article.current_position}
              </span>
            )}
            {article.total_points && (
              <span className="total-points">
                Total: {article.total_points} pts
              </span>
            )}
          </div>
          
          <div className="article-body">
            {renderArticleWithTable()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleDetail;

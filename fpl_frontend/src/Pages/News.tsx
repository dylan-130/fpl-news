import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../Components/Navbar/Navbar';
import ArticleDetail from '../Components/ArticleDetail/ArticleDetail';
import '../styles/Global.css';
import '../Components/Navbar/Navbar.css';
import '../styles/News.css';
import Button from '../Components/Button/Button';

interface Article {
  headline: string;
  body: string;
  league_name: string;
  league_id: number;
  gameweek: number;
  position_change: number;
}

const News = () => {
  const navigate = useNavigate();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  const openArticleDetail = (article: Article) => {
    setSelectedArticle(article);
  };

  const closeArticleDetail = () => {
    setSelectedArticle(null);
  };

  const getPositionArrow = (positionChange: number) => {
    if (positionChange > 0) return "↗";
    if (positionChange < 0) return "↘";
    return "→";
  };

  const getArticleSynopsis = (fullBody: string) => {
    // Get first sentence or first 150 characters, whichever is shorter
    const firstSentence = fullBody.split('.')[0];
    if (firstSentence.length <= 150) {
      return firstSentence + '.';
    }
    return fullBody.substring(0, 150) + '...';
  };

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const playerId = localStorage.getItem('playerId');
        if (!playerId) {
          throw new Error('Player ID not found. Please try connecting again.');
        }

        // Fetch news articles from the API
        const teamName = localStorage.getItem('teamName') || 'Your Team';
        const managerName = localStorage.getItem('playerName') || 'Manager';
        
        const response = await fetch(`http://127.0.0.1:8000/api/generate_league_news/?playerId=${playerId}&teamName=${encodeURIComponent(teamName)}&managerName=${encodeURIComponent(managerName)}`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to fetch league news');
        }
        
        const data = await response.json();
        console.log("News articles received:", data);
        
        if (data.articles && Array.isArray(data.articles)) {
          setArticles(data.articles);
        } else {
          throw new Error('Invalid news data format');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load news');
        console.error("Error fetching news:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  if (loading) return <div className="loading">Generating your league news...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="page-container news-page-container">
      <Navbar />
      
      <div className="news-page">
        <div className="news-header">
          <h1>📰 Your League News</h1>
          <p>Personalized updates from all your leagues</p>
        </div>

        <div className="articles-container">
          {articles.length === 0 ? (
            <div className="no-articles">
              <p>No league news available at the moment. Check back after the next gameweek!</p>
            </div>
                 ) : (
                   articles.map((article, index) => (
                     <article key={index} className="news-article">
                       <div className="article-header">
                         <h2>{article.headline}</h2>
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
                           {article.position_change !== 0 && (
                             <span className={`position-change ${article.position_change > 0 ? 'positive' : 'negative'}`}>
                               {article.position_change > 0 ? '↗' : '↘'} {Math.abs(article.position_change)} places
                             </span>
                           )}
                         </div>
                       </div>
                       <div className="article-body">
                         <p>{getArticleSynopsis(article.body)}</p>
                       </div>
                       <div className="article-footer">
                         <Button
                           label="📖 Read Article"
                           onClick={() => openArticleDetail(article)}
                           className="read-article-button"
                         />
                       </div>
                     </article>
                   ))
                 )}
        </div>

        <div className="news-actions">
          <Button 
            label="🔙 Back to Team" 
            onClick={() => navigate('/connect')}
            className="back-button"
          />
          <Button 
            label="🎯 Get Bet-Builder" 
            onClick={() => navigate('/bet-builder')}
            className="bet-builder-button"
          />
        </div>
      </div>
      
      {selectedArticle && (
        <ArticleDetail
          article={selectedArticle}
          onClose={closeArticleDetail}
        />
      )}
    </div>
  );
};

export default News;

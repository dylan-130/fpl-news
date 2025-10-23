# FPL News - AI-Powered Fantasy Premier League News and Betting Platform

A sophisticated web application that combines Fantasy Premier League (FPL) team analysis with AI-powered article generation and betting suggestions. Built with Django backend and React frontend, featuring machine learning for personalized bet generation.

## 🚀 Features

### Core Functionality
- **FPL Team Integration**: Connect your FPL team and view your current squad
- **AI-Powered Bet Builder**: Sophisticated ML system that generates personalized betting suggestions
- **AI-Powered League News Articles**: News articles generated automatically for all your leagues so you can stay two steps ahead of the curve!
- **User-Specific Learning**: Tracks betting history to improve suggestions over time
- **Dynamic Odds Adjustment**: "I'm Feeling Lucky" system for risk adjustment
- **Professional Bet Slip**: Complete betting interface with stake management

### Technical Highlights
- **Machine Learning Backend**: Sophisticated player analysis and odds generation
- **User Behavior Learning**: Personalized betting patterns based on historical data
- **Real-time FPL Data**: Live integration with Fantasy Premier League API
- **Responsive Design**: Modern, engaging UI with animations and professional styling
- **Scalable Architecture**: Django REST API with React frontend

## 🏗️ Architecture

### Backend (Django)
```
fpl_backend/
├── api/
│   ├── views.py          # API endpoints
│   ├── services.py       # FPL API integration
│   ├── ml_models.py      # Machine learning system
│   └── urls.py           # URL routing
├── fpl_backend/
│   ├── settings.py       # Django configuration
│   └── urls.py           # Main URL routing
└── manage.py
```

### Frontend (React + TypeScript)
```
fpl_frontend/
├── src/
│   ├── Pages/
│   │   ├── Home.tsx          # Landing page
│   │   ├── Connect.tsx       # Team connection
│   │   ├── BetBuilder.tsx    # Bet builder interface
│   │   └── BetReceipt.tsx    # Bet confirmation
│   ├── Components/
│   │   ├── Button/
│   │   ├── Navbar/
│   │   └── PlayerCard/
│   └── styles/
└── package.json
```

## 🧠 Machine Learning System

### Player Analysis
- **Profile Classification**: High/Mid/Low profile players based on performance
- **Position Analysis**: Different betting strategies for different positions
- **Captain/Vice-Captain Logic**: Special consideration for team leadership

### Bet Generation Algorithm
1. **Team Composition Analysis**: Analyzes your FPL team structure
2. **Player Profile Matching**: Matches players to betting profiles
3. **Historical Learning**: Uses your betting history to adjust baseline odds
4. **Luck Level Adjustment**: Dynamic odds adjustment based on risk preference
5. **Multi-leg Bet Creation**: Generates 4-6 leg bets with optimal combinations

### User Learning Features
- **Betting History Tracking**: Records all placed bets
- **Pattern Recognition**: Learns user preferences over time
- **Odds Personalization**: Adjusts baseline odds based on user behavior
- **Risk Profile Adaptation**: Adapts to user's risk tolerance

## 🎯 Bet Types Supported

- **Goal Scorer**: Player to score goals
- **Assist**: Player to provide assists
- **Clean Sheet**: Defensive players to keep clean sheets
- **Bonus Points**: High-profile players to earn bonus points
- **Multiple Goals**: Players to score multiple goals
- **Man of the Match**: Players to win MOTM awards

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd fpl_backend
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

### Frontend Setup
```bash
cd fpl_frontend
npm install
npm run dev
```

### Environment Variables
Create a `.env` file in the backend directory:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📱 Usage Flow

1. **Connect Your Team**: Enter your FPL team name and full name
2. **View Your Squad**: See your current FPL team with player details
3. **Generate Bets**: Click "Confirm & Get Bet-Builder" to generate AI suggestions
4. **Adjust Risk**: Use "I'm Feeling Lucky" buttons to adjust odds
5. **Place Bet**: Set your stake and place the bet
6. **Get Receipt**: View your bet confirmation and receipt

## 🎨 UI/UX Features

- **Consistent Color Palette**: Professional blue-purple gradient theme
- **Smooth Animations**: Engaging transitions and hover effects
- **Responsive Design**: Works perfectly on all device sizes
- **Interactive Elements**: Dynamic buttons and real-time updates
- **Professional Bet Slip**: Industry-standard betting interface

## 🔧 Technical Implementation

### API Endpoints
- `GET /api/get_player_id/` - Get FPL player ID
- `GET /api/async_get_team_data/` - Fetch team data
- `GET /api/generate_bet_suggestions/` - Generate ML-powered bets
- `GET /api/adjust_odds/` - Adjust odds based on luck level
- `POST /api/place_bet/` - Place a bet and record it

### ML Model Features
- **Player Profile Classification**: Automatic player categorization
- **Odds Calculation**: Sophisticated odds generation algorithm
- **User History Learning**: Personalized betting patterns
- **Risk Adjustment**: Dynamic odds modification

### Data Storage
- **User Betting History**: JSON-based storage for user preferences
- **Player Profiles**: Cached player performance data
- **Bet Records**: Complete bet tracking and analysis

## 🎓 Professional Features

This project demonstrates:
- **Full-Stack Development**: Django + React architecture
- **Machine Learning Integration**: Sophisticated ML algorithms
- **API Design**: RESTful API with proper error handling
- **User Experience**: Professional, engaging interface
- **Data Analysis**: Real-time data processing and analysis
- **Scalable Architecture**: Modular, maintainable codebase

## 🔮 Future Enhancements

- **Real-time Odds Updates**: Live odds from betting providers
- **Advanced ML Models**: Deep learning for better predictions
- **Social Features**: Share bets with friends
- **Mobile App**: Native iOS/Android applications
- **Betting History Dashboard**: Detailed analytics and insights

## 📄 License

This project is for educational and portfolio purposes.

## 👨‍💻 Author

Built as a professional software engineering project showcasing advanced full-stack development skills, machine learning integration, and modern web technologies.

---

**Note**: This is a demonstration project. No real money betting is involved.

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './Pages/Home';
import Connect from './Pages/Connect';
import BetBuilder from './Pages/BetBuilder';
import BetReceipt from './Pages/BetReceipt';
import './styles/Global.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/connect" element={<Connect />} />
        <Route path="/bet-builder" element={<BetBuilder />} />
        <Route path="/bet-receipt" element={<BetReceipt />} />
      </Routes>
    </Router>
  );
}

export default App;
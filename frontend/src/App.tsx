// Main App Component

import React from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="App">
      <ChatInterface />
    </div>
  );
};

export default App;
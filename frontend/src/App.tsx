import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import TestPage from './pages/TestPage';
import './App.css'

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TestPage />} />
      </Routes>
    </Router>
  )
}

export default App

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DocumentTypeSelection from './pages/DocumentTypeSelection';
import InformedConsentPage from './pages/InformedConsentPage';
import SiteChecklistPage from './pages/SiteChecklistPage';
import './App.css'

const App: React.FC = () => {
  return (
    <div className="min-h-screen">
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/document-selection" element={<DocumentTypeSelection />} />
          <Route path="/informed-consent" element={<InformedConsentPage />} />
          <Route path="/site-checklist" element={<SiteChecklistPage />} />
        </Routes>
      </Router>
    </div>
  )
}

export default App

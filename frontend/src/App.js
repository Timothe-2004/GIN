import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import AdminSignup from './components/AdminSignup';
import AddFormation from './components/AddFormation';
import AddStage from './components/AddStage';
import AddRealisation from './components/AddRealisation';
import AddPartenaire from './components/AddPartenaire';
import AddService from './components/AddService';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<AdminSignup />} />
          <Route path="/add-formation" element={<AddFormation />} />
          <Route path="/add-stage" element={<AddStage />} />
          <Route path="/add-realisation" element={<AddRealisation />} />
          <Route path="/add-partenaire" element={<AddPartenaire />} />
          <Route path="/add-service" element={<AddService />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
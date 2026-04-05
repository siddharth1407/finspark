import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Requirements from './pages/Requirements';
import Configurations from './pages/Configurations';
import Simulation from './pages/Simulation';
import Adapters from './pages/Adapters';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/requirements" element={<Requirements />} />
          <Route path="/requirements/:id" element={<Requirements />} />
          <Route path="/configurations" element={<Configurations />} />
          <Route path="/configurations/:id" element={<Configurations />} />
          <Route path="/simulation" element={<Simulation />} />
          <Route path="/simulation/:configId" element={<Simulation />} />
          <Route path="/adapters" element={<Adapters />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

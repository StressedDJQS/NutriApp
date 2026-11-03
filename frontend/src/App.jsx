import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Foods from './pages/Foods';
import Recipes from './pages/Recipes';
import Menus from './pages/Menus'; 

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Foods />} />
          <Route path="recipes" element={<Recipes />} />
          <Route path="menus" element={<Menus />} /> {/* Añadir esta ruta */}
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
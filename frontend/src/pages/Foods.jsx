import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Plus, Search } from 'lucide-react';
import CreateFoodModal from '../components/CreateFoodModal';

export default function Foods() {
  const [foods, setFoods] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editData, setEditData] = useState(null);

  useEffect(() => { fetchFoods(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("¿Estás seguro de eliminar este alimento?")) return;
    try {
      await apiClient.delete(`/foods/${id}`);
      fetchFoods();
    } catch (error) { alert("Error eliminando alimento."); }
  };

  const fetchFoods = async () => {
    try {
      const response = await apiClient.get('/foods/');
      setFoods(response.data);
    } catch (error) { console.error(error); } 
    finally { setLoading(false); }
  };

  const filteredFoods = foods.filter(food => 
    food.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (food.category && food.category.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) return <div className="text-slate-500">Cargando catálogo...</div>;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
        <h3 className="text-lg font-bold text-slate-800">Catálogo de Víveres</h3>
        <div className="flex gap-4">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-2.5 text-slate-400" />
            <input type="text" placeholder="Buscar alimento..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2B6CB0]" />
          </div>
          <button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2 bg-[#2B6CB0] hover:bg-[#1A365D] text-white px-4 py-2 rounded-lg font-semibold transition-colors">
            <Plus className="w-4 h-4" /> Nuevo Alimento
          </button>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-100 text-slate-600 text-sm border-b border-slate-200">
              <th className="p-4 font-semibold">Alimento</th><th className="p-4 font-semibold">Categoría</th>
              <th className="p-4 font-semibold">Unidad</th><th className="p-4 font-semibold">Precio Ref.</th>
              <th className="p-4 font-semibold">Energía (kcal)</th>
              <th className="p-4 font-semibold">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredFoods.length === 0 ? (
              <tr><td colSpan="5" className="p-8 text-center text-slate-500">No hay alimentos.</td></tr>
            ) : (
              filteredFoods.map((food) => (
                <tr key={food.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-medium text-slate-800">{food.name}</td>
                  <td className="p-4"><span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold">{food.category || 'General'}</span></td>
                  <td className="p-4"><span className="font-mono bg-slate-100 px-2 py-1 rounded text-sm">{food.unit}</span></td>
                  <td className="p-4 text-slate-600 font-medium">S/. {food.unit_price} / {food.price_unit}</td>
                  <td className="p-4 text-slate-600">{food.calories} kcal</td>
                  <td className="p-4 flex gap-2 justify-end">
                    <button onClick={() => { setEditData(food); setIsModalOpen(true); }} className="text-blue-600 hover:text-blue-800 text-sm font-medium px-2">Editar</button>
                    <button onClick={() => handleDelete(food.id)} className="text-red-600 hover:text-red-800 text-sm font-medium px-2">Eliminar</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <CreateFoodModal 
          initialData={editData}
          onClose={() => { setIsModalOpen(false); setEditData(null); }} 
          onSuccess={() => { setIsModalOpen(false); setEditData(null); fetchFoods(); }} 
        />
      )}
    </div>
  );
}
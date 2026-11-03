import { useState } from 'react';
import { X } from 'lucide-react';
import { apiClient } from '../api/client';

export default function CreateFoodModal({ onClose, onSuccess, initialData = null }) {
  const [formData, setFormData] = useState(initialData || {
    name: '', category: '', unit: 'g', unit_price: 0, price_unit: 'kg',
    calories: 0, protein: 0, carbohydrates: 0, fats: 0, fiber: 0, sodium: 0
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (initialData?.id) {
        await apiClient.put(`/foods/${initialData.id}`, formData);
      } else {
        await apiClient.post('/foods/', formData);
      }
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error("Error guardando alimento:", error);
      alert("Hubo un error al guardar el alimento.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-slate-200 sticky top-0 bg-white">
          <h2 className="text-xl font-bold text-slate-800">
            {initialData ? 'Editar Alimento' : 'Registrar Nuevo Alimento'}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X className="w-6 h-6" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1">Nombre (*)</label>
              <input type="text" name="name" required value={formData.name} onChange={handleInputChange} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Categoría</label>
              <input type="text" name="category" value={formData.category} onChange={handleInputChange} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Unidad Física (*)</label>
              <select name="unit" value={formData.unit} onChange={handleInputChange} className="w-full border border-slate-300 rounded-lg px-3 py-2 bg-white">
                <option value="g">Gramos (g)</option><option value="kg">Kilogramos (kg)</option>
                <option value="ml">Mililitros (ml)</option><option value="l">Litros (l)</option>
                <option value="unidad">Unidad</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Precio Unitario (S/.) (*)</label>
              <input type="number" step="0.01" name="unit_price" required value={formData.unit_price} onChange={handleInputChange} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Por cada (Unidad Precio)</label>
              <select name="price_unit" value={formData.price_unit} onChange={handleInputChange} className="w-full border border-slate-300 rounded-lg px-3 py-2 bg-white">
                <option value="kg">Kilogramo (kg)</option><option value="l">Litro (l)</option>
                <option value="unidad">Unidad</option>
              </select>
            </div>
          </div>
          
          <h4 className="font-bold text-slate-800 border-b pb-2">Perfil Nutricional (por 100g/ml o 1 unidad)</h4>
          <div className="grid grid-cols-3 gap-4">
            {['calories', 'protein', 'carbohydrates', 'fats', 'fiber', 'sodium'].map((nut) => (
              <div key={nut}>
                <label className="block text-sm font-semibold text-slate-700 mb-1 capitalize">{nut}</label>
                <input type="number" step="0.01" name={nut} value={formData[nut]} onChange={handleInputChange} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
              </div>
            ))}
          </div>
          
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
            <button type="button" onClick={onClose} className="px-4 py-2 border border-slate-300 rounded-lg font-semibold text-slate-600 hover:bg-slate-50">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-[#2F855A] text-white rounded-lg font-semibold hover:bg-[#276749]">Guardar Alimento</button>
          </div>
        </form>
      </div>
    </div>
  );
}
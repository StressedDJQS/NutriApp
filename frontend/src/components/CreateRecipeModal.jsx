import { useState, useEffect } from 'react';
import { X, Trash2 } from 'lucide-react';
import { apiClient } from '../api/client';
import CreateFoodModal from './CreateFoodModal';

export default function CreateRecipeModal({ onClose, onSuccess, initialData = null, isEdit = false }) {
  const [foods, setFoods] = useState([]);
  const [showQuickFood, setShowQuickFood] = useState(false);
  
  // Si initialData existe (Heredar), precargamos los datos. Si no, usamos plantilla vacía.
  const [formData, setFormData] = useState(
    initialData ? {
      name: isEdit ? initialData.name : initialData.name + ' (Copia)',
      description: initialData.description || '',
      base_portions: initialData.base_portions || 1,
      ingredients: initialData.ingredients?.map(ing => ({
        food_id: ing.food?.id,
        quantity: ing.quantity
      })) || []
    } : { name: '', description: '', base_portions: 1, ingredients: [] }
  );

  useEffect(() => { fetchFoods(); }, []);

  const fetchFoods = async () => {
    try {
      const response = await apiClient.get('/foods/');
      setFoods(response.data);
    } catch (error) { console.error(error); }
  };

  const handleAddIngredient = () => {
    setFormData(prev => ({ ...prev, ingredients: [...prev.ingredients, { food_id: '', quantity: '' }] }));
  };

  const handleIngredientChange = (index, field, value) => {
    const newIngredients = [...formData.ingredients];
    newIngredients[index][field] = value;
    setFormData(prev => ({ ...prev, ingredients: newIngredients }));
  };

  const handleRemoveIngredient = (index) => {
    const newIngredients = formData.ingredients.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, ingredients: newIngredients }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.ingredients.length === 0) return alert("Añade al menos un ingrediente.");
    try {
      if (isEdit && initialData?.id) {
        await apiClient.put(`/recipes/${initialData.id}`, formData);
      } else {
        await apiClient.post('/recipes/', formData);
      }
      if (onSuccess) onSuccess();
    } catch (error) { alert("Error guardando receta."); }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center p-6 border-b border-slate-200 sticky top-0 bg-white z-10">
            <h2 className="text-xl font-bold text-slate-800">
                {isEdit ? 'Editar Receta' : initialData ? 'Heredar y Crear Receta' : 'Crear Receta'}
            </h2>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X className="w-6 h-6" /></button>
          </div>
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-semibold text-slate-700 mb-1">Nombre (*)</label>
                <input type="text" required value={formData.name} onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-semibold text-slate-700 mb-1">Descripción</label>
                <input type="text" value={formData.description} onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Porciones Base (*)</label>
                <input type="number" min="1" required value={formData.base_portions} onChange={e => setFormData(prev => ({ ...prev, base_portions: parseInt(e.target.value) }))} className="w-full border border-slate-300 rounded-lg px-3 py-2" />
              </div>
            </div>

            <div className="border-t border-slate-200 pt-4">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-4">
                    <h4 className="font-bold text-slate-800">Ingredientes</h4>
                    <button type="button" onClick={() => setShowQuickFood(true)} className="text-xs text-[#2B6CB0] font-bold hover:underline">
                        + Registrar alimento faltante
                    </button>
                </div>
                <button type="button" onClick={handleAddIngredient} className="text-sm bg-slate-100 text-slate-700 px-3 py-1 rounded border hover:bg-slate-200">+ Agregar Insumo</button>
              </div>
              {formData.ingredients.map((ing, idx) => (
                <div key={idx} className="flex gap-4 mb-3 items-center">
                  <select required value={ing.food_id} onChange={(e) => handleIngredientChange(idx, 'food_id', e.target.value)} className="flex-1 border border-slate-300 rounded-lg px-3 py-2 bg-white">
                    <option value="">Seleccione un alimento...</option>
                    {foods.map(f => <option key={f.id} value={f.id}>{f.name} ({f.unit})</option>)}
                  </select>
                  <input type="number" step="0.01" required placeholder="Cantidad" value={ing.quantity} onChange={(e) => handleIngredientChange(idx, 'quantity', e.target.value)} className="w-32 border border-slate-300 rounded-lg px-3 py-2" />
                  <button type="button" onClick={() => handleRemoveIngredient(idx)} className="text-red-500 hover:text-red-700"><Trash2 className="w-5 h-5" /></button>
                </div>
              ))}
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
              <button type="button" onClick={onClose} className="px-4 py-2 border border-slate-300 rounded-lg font-semibold text-slate-600 hover:bg-slate-50">Cancelar</button>
              <button type="submit" className="px-4 py-2 bg-[#2B6CB0] text-white rounded-lg font-semibold hover:bg-[#1A365D]">Guardar Receta</button>
            </div>
          </form>
        </div>
      </div>

      {showQuickFood && (
        <div className="z-[60] relative">
          <CreateFoodModal 
            onClose={() => setShowQuickFood(false)}
            onSuccess={() => { setShowQuickFood(false); fetchFoods(); }}
          />
        </div>
      )}
    </>
  );
}
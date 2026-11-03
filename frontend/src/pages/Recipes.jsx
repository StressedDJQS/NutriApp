import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Plus, X, Calculator, BookOpen, Copy } from 'lucide-react';
import CreateRecipeModal from '../components/CreateRecipeModal';

export default function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const [foods, setFoods] = useState([]); // Añadido para cruzar IDs de alimentos
  const [loading, setLoading] = useState(true);
  const [isEditMode, setIsEditMode] = useState(false);
  
  // Estados para controlar modales
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inheritData, setInheritData] = useState(null); // Datos para clonar
  const [viewRecipe, setViewRecipe] = useState(null);
  const [scaleRecipe, setScaleRecipe] = useState(null);
  const [targetPortions, setTargetPortions] = useState(1);

  useEffect(() => { 
    fetchRecipes(); 
    fetchFoods();
  }, []);

  const fetchRecipes = async () => {
    try {
      const response = await apiClient.get('/recipes/');
      setRecipes(response.data);
    } catch (error) { console.error(error); } 
    finally { setLoading(false); }
  };

  const fetchFoods = async () => {
    try {
      const response = await apiClient.get('/foods/');
      setFoods(response.data);
    } catch (error) { console.error(error); }
  };

  // Funciones para cruzar ID del ingrediente con el catálogo de alimentos
  const getFoodName = (foodId) => {
    const food = foods.find(f => f.id === foodId);
    return food ? food.name : `Cargando... (ID: ${foodId})`;
  };

  const getFoodUnit = (foodId) => {
    const food = foods.find(f => f.id === foodId);
    return food ? food.unit : '';
  };

  const handleOpenScale = (recipe) => {
    setScaleRecipe(recipe);
    setTargetPortions(recipe.base_portions);
  };

  const handleInherit = (recipe) => {
    setInheritData(recipe);
    setIsModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Eliminar esta receta permanentemente?")) return;
    try {
      await apiClient.delete(`/recipes/${id}`);
      fetchRecipes();
    } catch (error) { alert("Error eliminando receta."); }
  };

  if (loading) return <div className="text-slate-500 p-6">Cargando recetas...</div>;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden relative">
      <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
        <h3 className="text-lg font-bold text-slate-800">Recetas y Preparaciones</h3>
        <button onClick={() => { setInheritData(null); setIsModalOpen(true); }} className="flex items-center gap-2 bg-[#2B6CB0] hover:bg-[#1A365D] text-white px-4 py-2 rounded-lg font-semibold transition-colors">
          <Plus className="w-4 h-4" /> Nueva Receta
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-100 text-slate-600 text-sm border-b border-slate-200">
              <th className="p-4 font-semibold">Nombre de la Receta</th>
              <th className="p-4 font-semibold">Porciones Base</th>
              <th className="p-4 font-semibold">N° Ingredientes</th>
              <th className="p-4 font-semibold text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {recipes.length === 0 ? (
              <tr><td colSpan="4" className="p-8 text-center text-slate-500">No hay recetas registradas.</td></tr>
            ) : (
              recipes.map((recipe) => (
                <tr key={recipe.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="p-4 font-medium text-slate-800">{recipe.name}</td>
                  <td className="p-4 text-slate-600">{recipe.base_portions}</td>
                  <td className="p-4">
                    <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full text-xs font-semibold shadow-sm">
                      {recipe.ingredients?.length || 0} insumos
                    </span>
                  </td>
                  <td className="p-4 flex gap-2 justify-end">
                    <button 
                      onClick={() => handleInherit(recipe)} 
                      className="flex items-center gap-1 text-emerald-600 hover:text-emerald-800 text-sm font-medium border border-emerald-200 px-3 py-1 rounded hover:bg-emerald-50 bg-white" title="Crear copia modificable">
                      <Copy className="w-3 h-3"/> Heredar
                    </button>
                    <button 
                      onClick={() => setViewRecipe(recipe)} 
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium border border-blue-200 px-3 py-1 rounded hover:bg-blue-50 bg-white">
                      Ver detalle
                    </button>
                    <button 
                      onClick={() => handleOpenScale(recipe)} 
                      className="text-amber-600 hover:text-amber-800 text-sm font-medium border border-amber-200 px-3 py-1 rounded hover:bg-amber-50 bg-white">
                      Escalar
                    </button>
                    <button 
                      onClick={() => { setInheritData(recipe); setIsEditMode(true); setIsModalOpen(true); }} 
                      className="text-indigo-600 hover:text-indigo-800 text-sm border border-indigo-200 px-3 py-1 rounded">
                      Editar
                    </button>
                    <button 
                      onClick={() => handleDelete(recipe.id)} 
                      className="text-red-600 hover:text-red-800 text-sm border border-red-200 px-3 py-1 rounded">
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de Creación / Herencia */}
      {isModalOpen && (
        <CreateRecipeModal 
          initialData={inheritData}
          isEdit={isEditMode}
          onClose={() => { setIsModalOpen(false); setInheritData(null); setIsEditMode(false); }}
          onSuccess={() => { setIsModalOpen(false); setInheritData(null); setIsEditMode(false); fetchRecipes(); }}
        />
      )}

      {/* Modal Ver Detalles */}
      {viewRecipe && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-slate-200 bg-slate-50">
              <h2 className="text-xl font-bold flex items-center gap-2 text-slate-800">
                <BookOpen className="text-blue-600 w-5 h-5" /> Detalles de Receta
              </h2>
              <button onClick={() => setViewRecipe(null)} className="text-slate-400 hover:text-slate-600"><X className="w-6 h-6" /></button>
            </div>
            <div className="p-6">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-slate-800 mb-2">{viewRecipe.name}</h3>
                <p className="text-slate-600">{viewRecipe.description || 'Sin descripción detallada.'}</p>
                <div className="mt-4 inline-block bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg font-semibold">
                  Rinde para: {viewRecipe.base_portions} porciones
                </div>
              </div>
              <h4 className="font-bold text-slate-800 mb-3 border-b pb-2">Ingredientes</h4>
              <ul className="space-y-2">
                {viewRecipe.ingredients?.map((ing, idx) => (
                  <li key={idx} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="font-medium text-slate-700">
                      {ing.food?.name}
                    </span>
                    <span className="font-bold text-slate-600 bg-white px-3 py-1 rounded border border-slate-200">
                      {ing.quantity} {ing.food?.unit}
                    </span>
                  </li>
                ))}
                {!viewRecipe.ingredients?.length && <li className="text-slate-500">No hay ingredientes registrados.</li>}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Modal Escalar Receta */}
      {scaleRecipe && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-slate-200 bg-slate-50">
              <h2 className="text-xl font-bold flex items-center gap-2 text-slate-800">
                <Calculator className="text-amber-600 w-5 h-5" /> Calculadora de Porciones
              </h2>
              <button onClick={() => setScaleRecipe(null)} className="text-slate-400 hover:text-slate-600"><X className="w-6 h-6" /></button>
            </div>
            <div className="p-6">
              <h3 className="text-xl font-bold text-slate-800 mb-4">{scaleRecipe.name}</h3>
              
              <div className="flex items-center gap-4 bg-amber-50 p-4 rounded-lg border border-amber-200 mb-6">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Porciones deseadas:</label>
                  <input
                    type="number"
                    min="1"
                    value={targetPortions}
                    onChange={(e) => setTargetPortions(Number(e.target.value) || 1)}
                    className="w-24 p-2 border rounded"
                  />
                </div>
                <div className="text-sm text-slate-600 pt-5">
                  (Receta original: {scaleRecipe.base_portions} porciones)
                </div>
              </div>

              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-100 text-slate-600 text-sm border-b border-slate-200">
                    <th className="p-3 font-semibold">Ingrediente</th>
                    <th className="p-3 font-semibold text-right">Cant. Original</th>
                    <th className="p-3 font-semibold text-right text-amber-700">Cant. Ajustada</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {scaleRecipe.ingredients?.map((ing, idx) => {
                    const factor = targetPortions / scaleRecipe.base_portions;
                    const newQuantity = (ing.quantity * factor).toFixed(2);
                    
                    return (
                      <tr key={idx}>
                        <td className="p-3 text-slate-800 font-medium">
                          {ing.food?.name} 
                        </td>
                        <td className="p-3 text-right text-slate-500">
                          {ing.quantity} {ing.food?.unit}
                        </td>
                        <td className="p-3 text-right font-bold text-amber-700 bg-amber-50/30">
                          {newQuantity} {ing.food?.unit}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              
              <div className="mt-6 flex justify-end gap-3">
                <button 
                  onClick={() => setScaleRecipe(null)} 
                  className="px-4 py-2 text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 font-medium"
                >
                  Cerrar
                </button>
                <button 
                  onClick={() => {
                    // 1. Calculamos los nuevos datos
                    const factor = targetPortions / scaleRecipe.base_portions;
                    const scaledData = {
                      ...scaleRecipe,
                      name: `${scaleRecipe.name} (Escalada a ${targetPortions} porciones)`,
                      base_portions: targetPortions,
                      ingredients: scaleRecipe.ingredients.map(ing => ({
                        ...ing,
                        quantity: Number((ing.quantity * factor).toFixed(2))
                      }))
                    };
                    
                    // 2. Cerramos este modal y abrimos el de creación con los datos ajustados
                    setScaleRecipe(null);
                    setInheritData(scaledData);
                    setIsModalOpen(true);
                  }} 
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 font-medium flex items-center gap-2"
                >
                  Guardar como nueva receta
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
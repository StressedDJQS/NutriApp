import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Plus, X, CalendarDays, ClipboardList, Activity, Target, Flame, PieChart, ShoppingCart } from 'lucide-react';
import CreateRecipeModal from '../components/CreateRecipeModal';

export default function Menus() {
  const [menus, setMenus] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [editMenuId, setEditMenuId] = useState(null);
  
  // Estados de modales
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [showQuickRecipe, setShowQuickRecipe] = useState(false);
  const [activeReport, setActiveReport] = useState(null); // { type: 'adequacy' | 'groceries', data: {} }
  
  const [formData, setFormData] = useState({ name: '', target_calories: 2000, schedule: [] });

  useEffect(() => {
    fetchMenus();
    fetchRecipes();
  }, []);

  const fetchMenus = async () => {
    try {
      const res = await apiClient.get('/menus/');
      setMenus(res.data);
    } catch (error) { console.error(error); }
  };

  const fetchRecipes = async () => {
    try {
      const res = await apiClient.get('/recipes/');
      setRecipes(res.data);
    } catch (error) { console.error(error); }
  };

  const handleAddSchedule = () => {
    setFormData(prev => ({
      ...prev, schedule: [...prev.schedule, { day_of_week: 'Lunes', meal_time: 'Almuerzo', recipe_id: '', portions: 1 }]
    }));
  };

  const handleScheduleChange = (index, field, value) => {
    const newSched = [...formData.schedule];
    newSched[index][field] = value;
    setFormData(prev => ({ ...prev, schedule: newSched }));
  };

  const handleDeleteMenu = async (id) => {
    if (!window.confirm("¿Eliminar menú?")) return;
    try {
      await apiClient.delete(`/menus/${id}`);
      fetchMenus();
    } catch (error) { alert("Error al eliminar"); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.schedule.length === 0) return alert("Agrega al menos una comida.");
    try {
      if (editMenuId) {
        await apiClient.put(`/menus/${editMenuId}`, formData);
      } else {
        await apiClient.post('/menus/', formData);
      }
      setIsCreateOpen(false);
      setEditMenuId(null);
      fetchMenus();
      setFormData({ name: '', target_calories: 2000, schedule: [] });
    } catch (error) { console.error(error); }
  };

  const handleEditMenu = (menu) => {
    setFormData({
      name: menu.name,
      target_calories: menu.target_calories,
      schedule: menu.schedule.map(s => ({
        day_of_week: s.day_of_week,
        meal_time: s.meal_time,
        recipe_id: s.recipe.id,
        portions: s.portions
      }))
    });
    setEditMenuId(menu.id);
    setIsCreateOpen(true);
  };

  const viewReport = async (menuId, type) => {
    try {
      const endpoint = type === 'adequacy' ? `/menus/${menuId}/adequacy` : `/menus/${menuId}/groceries`;
      const res = await apiClient.get(endpoint);
      setActiveReport({ type, data: res.data });
    } catch (error) { console.error(error); }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
        <h3 className="text-lg font-bold text-slate-800">Menús y Cronogramas Semanales</h3>
        <button onClick={() => setIsCreateOpen(true)} className="flex items-center gap-2 bg-[#2B6CB0] text-white px-4 py-2 rounded-lg font-semibold hover:bg-[#1A365D] transition-colors">
          <CalendarDays className="w-4 h-4" /> Planificar Menú
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-100 text-slate-600 text-sm border-b border-slate-200">
              <th className="p-4 font-semibold">Nombre del Menú</th>
              <th className="p-4 font-semibold">Meta Calórica</th>
              <th className="p-4 font-semibold">Comidas Programadas</th>
              <th className="p-4 font-semibold text-right">Reportes Generados</th>
            </tr>
          </thead>
          <tbody>
            {menus.length === 0 ? (
              <tr><td colSpan="4" className="p-8 text-center text-slate-500">No hay menús registrados.</td></tr>
            ) : (
              menus.map((m) => (
                <tr key={m.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="p-4 font-medium text-slate-800">{m.name}</td>
                  <td className="p-4 text-slate-600">{m.target_calories} kcal/día</td>
                  <td className="p-4 text-slate-600">
                    <span className="bg-slate-100 px-2 py-1 rounded text-sm font-medium border border-slate-200">
                      {m.schedule.length} asignaciones
                    </span>
                  </td>
                  <td className="p-4 flex gap-2 justify-end">
                    <button onClick={() => viewReport(m.id, 'adequacy')} className="flex items-center gap-1 text-[#2F855A] hover:bg-green-50 px-3 py-1.5 rounded border border-green-200 text-sm font-medium transition-colors bg-white">
                        <Activity className="w-4 h-4" /> Adecuación
                    </button>
                    <button onClick={() => viewReport(m.id, 'groceries')} className="flex items-center gap-1 text-[#2B6CB0] hover:bg-blue-50 px-3 py-1.5 rounded border border-blue-200 text-sm font-medium transition-colors bg-white">
                        <ShoppingCart className="w-4 h-4" /> Víveres
                    </button>
                    <button onClick={() => handleEditMenu(m)} className="text-indigo-600 hover:text-indigo-800 text-sm border border-indigo-200 px-3 py-1.5 rounded bg-white font-medium">
                        Editar
                    </button>
                    <button onClick={() => handleDeleteMenu(m.id)} className="text-red-600 hover:text-red-800 text-sm border border-red-200 px-3 py-1.5 rounded bg-white font-medium">
                        Eliminar
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Crear Menú */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b border-slate-200 sticky top-0 bg-white z-10">
              <h2 className="text-xl font-bold text-slate-800">
                {editMenuId ? 'Editar Cronograma Semanal' : 'Planificar Cronograma Semanal'}
              </h2>
              <button onClick={() => setIsCreateOpen(false)}><X className="w-6 h-6 text-slate-400 hover:text-slate-600" /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-6 bg-slate-50 p-4 rounded-lg border border-slate-200">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Nombre (Ej: Semana 1 - Octubre)</label>
                  <input type="text" required value={formData.name} onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))} className="w-full border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-[#2B6CB0] outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Meta Calórica Diaria (Kcal)</label>
                  <input type="number" required value={formData.target_calories} onChange={e => setFormData(prev => ({ ...prev, target_calories: e.target.value }))} className="w-full border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-[#2B6CB0] outline-none" />
                </div>
              </div>

              <div className="pt-2">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-4">
                    <h4 className="font-bold text-slate-800 text-lg">Programación de Comidas</h4>
                    <button type="button" onClick={() => setShowQuickRecipe(true)} className="text-sm text-[#2B6CB0] font-bold hover:underline">
                      + Registrar receta faltante
                    </button>
                  </div>
                  <button type="button" onClick={handleAddSchedule} className="flex items-center gap-1 text-sm bg-[#2F855A] text-white px-3 py-1.5 rounded-lg font-medium hover:bg-[#276749] transition-colors">
                    <Plus className="w-4 h-4" /> Asignar Comida
                  </button>
                </div>

                <div className="space-y-3">
                  {formData.schedule.map((item, idx) => (
                    <div key={idx} className="flex gap-3 items-center bg-white p-3 rounded-lg border border-slate-200 shadow-sm hover:border-[#2B6CB0] transition-colors">
                      <select value={item.day_of_week} onChange={e => handleScheduleChange(idx, 'day_of_week', e.target.value)} className="w-32 border border-slate-300 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white outline-none">
                        {['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'].map(d => <option key={d}>{d}</option>)}
                      </select>
                      <select value={item.meal_time} onChange={e => handleScheduleChange(idx, 'meal_time', e.target.value)} className="w-36 border border-slate-300 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white outline-none">
                        {['Desayuno','Almuerzo','Cena','Refrigerio'].map(m => <option key={m}>{m}</option>)}
                      </select>
                      <select required value={item.recipe_id} onChange={e => handleScheduleChange(idx, 'recipe_id', e.target.value)} className="flex-1 border border-slate-300 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white outline-none">
                        <option value="">Seleccione Receta...</option>
                        {recipes.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                      </select>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-slate-500">Porc.</span>
                        <input type="number" min="1" value={item.portions} onChange={e => handleScheduleChange(idx, 'portions', e.target.value)} className="w-20 border border-slate-300 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white outline-none text-center" />
                      </div>
                      <button type="button" onClick={() => { const s = [...formData.schedule]; s.splice(idx,1); setFormData(p=>({...p, schedule: s}))}} className="text-slate-400 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition-colors">
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                  {formData.schedule.length === 0 && (
                    <div className="text-center p-8 text-slate-500 border-2 border-dashed border-slate-200 rounded-lg">
                      No hay comidas programadas. Haz clic en "Asignar Comida" para empezar.
                    </div>
                  )}
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-6 border-t border-slate-200">
                <button type="button" onClick={() => setIsCreateOpen(false)} className="px-5 py-2.5 border border-slate-300 rounded-lg font-semibold text-slate-600 hover:bg-slate-50">Cancelar</button>
                <button type="submit" className="px-5 py-2.5 bg-[#2B6CB0] text-white rounded-lg font-semibold hover:bg-[#1A365D]">Guardar Menú</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Visores de Reportes Mejorados */}
      {activeReport && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[90vh]">
            <div className="flex justify-between items-center p-6 border-b border-slate-100">
              <h2 className="text-xl font-bold flex items-center gap-3 text-slate-800">
                {activeReport.type === 'adequacy' ? (
                  <><div className="p-2 bg-green-100 rounded-lg"><Activity className="text-green-600 w-6 h-6"/></div> Reporte de Adecuación Nutricional</>
                ) : (
                  <><div className="p-2 bg-blue-100 rounded-lg"><ClipboardList className="text-blue-600 w-6 h-6"/></div> Consolidado de Víveres</>
                )}
              </h2>
              <button onClick={() => setActiveReport(null)} className="text-slate-400 hover:text-slate-700 bg-slate-50 hover:bg-slate-100 p-2 rounded-full transition-colors"><X className="w-5 h-5" /></button>
            </div>
            
            <div className="p-6 overflow-y-auto">
              {activeReport.type === 'adequacy' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 flex items-center gap-4">
                      <div className="bg-white p-3 rounded-full shadow-sm border border-slate-100"><Target className="w-6 h-6 text-indigo-500" /></div>
                      <div>
                        <p className="text-sm font-semibold text-slate-500">Meta Planificada</p>
                        <p className="text-2xl font-bold text-slate-800">{activeReport.data.target_calories} <span className="text-sm font-medium text-slate-500">kcal</span></p>
                      </div>
                    </div>
                    <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 flex items-center gap-4">
                      <div className="bg-white p-3 rounded-full shadow-sm border border-slate-100"><Flame className="w-6 h-6 text-orange-500" /></div>
                      <div>
                        <p className="text-sm font-semibold text-slate-500">Energía Consolidada</p>
                        <p className="text-2xl font-bold text-slate-800">{activeReport.data.total_calories} <span className="text-sm font-medium text-slate-500">kcal</span></p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                    <div className="flex justify-between items-end mb-2">
                      <div className="flex items-center gap-2">
                        <PieChart className="w-5 h-5 text-slate-400" />
                        <span className="font-semibold text-slate-700">Porcentaje de Adecuación</span>
                      </div>
                      <span className="text-3xl font-black text-slate-800">{activeReport.data.adequacy_percentage}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-4 mt-4 overflow-hidden border border-slate-200">
                      <div 
                        className={`h-4 rounded-full transition-all duration-1000 ${activeReport.data.status === 'Óptimo' ? 'bg-green-500' : 'bg-red-500'}`} 
                        style={{ width: `${Math.min(activeReport.data.adequacy_percentage, 100)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-slate-400 mt-2 text-right">Regla de oro institucional: 90% - 110%</p>
                  </div>

                  <div className={`p-4 rounded-xl font-bold text-center flex items-center justify-center gap-2 shadow-sm border ${activeReport.data.status === 'Óptimo' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'}`}>
                    {activeReport.data.status === 'Óptimo' ? '✓ CUMPLE CON EL REQUERIMIENTO (ÓPTIMO)' : '⚠ FUERA DEL RANGO PERMITIDO (REVISAR MENÚ)'}
                  </div>
                </div>
              )}

              {activeReport.type === 'groceries' && (
                <div>
                  <div className="mb-6 p-6 bg-gradient-to-r from-[#2B6CB0] to-[#1A365D] text-white rounded-xl shadow-md flex justify-between items-center">
                    <div>
                      <p className="text-blue-100 font-medium text-sm mb-1">Costo Estimado Total</p>
                      <h3 className="text-3xl font-bold">S/. {activeReport.data.total_menu_cost}</h3>
                    </div>
                    <ShoppingCart className="w-12 h-12 text-blue-200 opacity-80" />
                  </div>
                  
                  <div className="border border-slate-200 rounded-xl overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-50 text-slate-600 text-sm border-b border-slate-200">
                          <th className="p-4 font-semibold">Insumo / Categoría</th>
                          <th className="p-4 font-semibold text-center">Req. Consolidado</th>
                          <th className="p-4 font-semibold text-right">Costo Estimado</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {activeReport.data.items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-slate-50 transition-colors">
                            <td className="p-4">
                              <p className="font-semibold text-slate-800">{item.food_name}</p>
                              <span className="inline-block mt-1 bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded font-medium border border-blue-100">
                                {item.category || 'General'}
                              </span>
                            </td>
                            <td className="p-4 text-center">
                              <span className="font-mono bg-slate-100 text-slate-700 px-3 py-1 rounded-md text-sm border border-slate-200">
                                {item.total_quantity} {item.unit}
                              </span>
                            </td>
                            <td className="p-4 font-bold text-slate-700 text-right">
                              S/. {item.estimated_cost}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal Rápido de Receta */}
      {showQuickRecipe && (
        <div className="z-[60] relative">
          <CreateRecipeModal 
            onClose={() => setShowQuickRecipe(false)}
            onSuccess={() => { setShowQuickRecipe(false); fetchRecipes(); }}
          />
        </div>
      )}
    </div>
  );
}
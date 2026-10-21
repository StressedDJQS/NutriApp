"""
Vista y componentes para la gestión de recetas y preparaciones (HU-02, T05-T09).
Incluye selector de ingredientes real, cálculo proporcional en tiempo real,
escalado de porciones y reutilización de recetas.
"""

from typing import Optional, List, Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QMessageBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QSplitter,
    QFrame,
    QTextEdit,
    QScrollArea,
)

from src.models.food import Food
from src.models.recipe import Recipe, RecipeIngredient
from src.services.food_service import FoodService
from src.services.recipe_service import (
    RecipeService,
    RecipeValidationError,
    DuplicateRecipeError,
)
from src.services.nutrition_calc import calculate_recipe_totals, RecipeTotals
from src.services.unit_converter import are_units_compatible, normalize_unit_name


class RecipeFormDialog(QDialog):
    """Diálogo modal para crear y editar recetas con selector de ingredientes real."""

    def __init__(
        self,
        food_service: FoodService,
        recipe_service: RecipeService,
        parent: Optional[QWidget] = None,
        recipe: Optional[Recipe] = None,
    ):
        super().__init__(parent)
        self.food_service = food_service
        self.recipe_service = recipe_service
        self.recipe = recipe
        self.is_edit = recipe is not None
        self.ingredients_buffer: List[RecipeIngredient] = []

        self.setWindowTitle("Editar Receta" if self.is_edit else "Crear Nueva Receta")
        self.resize(780, 620)
        self.init_ui()

        if self.is_edit and self.recipe:
            self.load_recipe_data(self.recipe)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # 1. Datos Generales de la Receta
        gen_group = QGroupBox("Datos de la Receta")
        gen_layout = QFormLayout(gen_group)
        gen_layout.setSpacing(8)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: Arroz con Pollo, Guiso de Lentejas, Sopa de Verduras...")

        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Descripción breve o recomendaciones de preparación (opcional)...")

        self.input_portions = QSpinBox()
        self.input_portions.setRange(1, 10000)
        self.input_portions.setValue(4)
        self.input_portions.setSuffix(" porciones")
        self.input_portions.valueChanged.connect(self._recalculate_preview)

        gen_layout.addRow("Nombre de la receta (*):", self.input_name)
        gen_layout.addRow("Descripción:", self.input_desc)
        gen_layout.addRow("Número de porciones base (*):", self.input_portions)

        main_layout.addWidget(gen_group)

        # 2. Selector e Inserción de Ingredientes desde Catálogo Real
        ing_group = QGroupBox("Ingredientes de la Receta")
        ing_layout = QVBoxLayout(ing_group)
        ing_layout.setSpacing(8)

        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.combo_foods = QComboBox()
        self.combo_foods.setMinimumWidth(260)
        self._populate_foods_combo()
        self.combo_foods.currentIndexChanged.connect(self._on_food_selected)

        self.input_quantity = QDoubleSpinBox()
        self.input_quantity.setRange(0.01, 999999.0)
        self.input_quantity.setDecimals(2)
        self.input_quantity.setValue(100.0)

        self.combo_unit = QComboBox()
        self.combo_unit.setMinimumWidth(80)

        self.btn_add_ing = QPushButton("➕ Agregar Ingrediente")
        self.btn_add_ing.setObjectName("btnPrimary")
        self.btn_add_ing.clicked.connect(self.on_add_ingredient)

        add_row.addWidget(QLabel("Alimento:"))
        add_row.addWidget(self.combo_foods, 2)
        add_row.addWidget(QLabel("Cantidad:"))
        add_row.addWidget(self.input_quantity, 1)
        add_row.addWidget(self.combo_unit, 1)
        add_row.addWidget(self.btn_add_ing)

        ing_layout.addLayout(add_row)

        # Trigger inicial para unidades del alimento seleccionado
        self._on_food_selected()

        # Tabla de ingredientes agregados
        self.table_ingredients = QTableWidget()
        self.table_ingredients.setColumnCount(5)
        self.table_ingredients.setHorizontalHeaderLabels([
            "Alimento",
            "Cantidad",
            "Unidad",
            "Costo Aprox.",
            "Acción",
        ])
        self.table_ingredients.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_ingredients.setColumnWidth(4, 100)
        self.table_ingredients.horizontalHeader().setMinimumSectionSize(70)
        self.table_ingredients.verticalHeader().setVisible(False)
        self.table_ingredients.verticalHeader().setDefaultSectionSize(42)
        self.table_ingredients.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_ingredients.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_ingredients.setMinimumHeight(175)
        ing_layout.addWidget(self.table_ingredients)

        main_layout.addWidget(ing_group)

        # 3. Resumen en Vivo
        preview_card = QFrame()
        preview_card.setObjectName("cardFrame")
        preview_layout = QHBoxLayout(preview_card)

        self.lbl_preview_cost = QLabel("Costo Total: S/. 0.00")
        self.lbl_preview_cost.setStyleSheet("font-weight: 700; color: #1A365D;")

        self.lbl_preview_portion_cost = QLabel("Costo por Porción: S/. 0.00")
        self.lbl_preview_portion_cost.setStyleSheet("font-weight: 700; color: #2B6CB0;")

        self.lbl_preview_calories = QLabel("Energía por Porción: 0.0 kcal")
        self.lbl_preview_calories.setStyleSheet("font-weight: 700; color: #2F855A;")

        preview_layout.addWidget(self.lbl_preview_cost)
        preview_layout.addWidget(self.lbl_preview_portion_cost)
        preview_layout.addWidget(self.lbl_preview_calories)
        main_layout.addWidget(preview_card)

        # Botones de Aceptación / Cancelación
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("btnSecondary")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Guardar Receta")
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def _populate_foods_combo(self):
        foods = self.food_service.list_foods()
        self.combo_foods.clear()
        for f in foods:
            display_text = f"{f.name} ({f.category or 'Sin categoría'})"
            self.combo_foods.addItem(display_text, userData=f.id)

    def _on_food_selected(self):
        food_id = self.combo_foods.currentData()
        if food_id is None:
            self.combo_unit.clear()
            return
        food = self.food_service.get_food_by_id(food_id)
        if not food:
            return

        self.combo_unit.clear()
        norm_unit = normalize_unit_name(food.unit)
        if norm_unit in ("g", "kg", "mg"):
            self.combo_unit.addItems(["g", "kg", "mg"])
            self.combo_unit.setCurrentText("g")
            self.input_quantity.setValue(100.0)
        elif norm_unit in ("ml", "l", "cc"):
            self.combo_unit.addItems(["ml", "l", "cc"])
            self.combo_unit.setCurrentText("ml")
            self.input_quantity.setValue(100.0)
        else:
            self.combo_unit.addItems(["unidad"])
            self.combo_unit.setCurrentText("unidad")
            self.input_quantity.setValue(1.0)

    def on_add_ingredient(self):
        food_id = self.combo_foods.currentData()
        if food_id is None:
            QMessageBox.warning(self, "Catálogo Vacío", "No hay alimentos en el catálogo para agregar.")
            return

        qty = self.input_quantity.value()
        if qty <= 0:
            QMessageBox.warning(self, "Cantidad Inválida", "La cantidad debe ser mayor a 0.")
            return

        unit = self.combo_unit.currentText().strip()

        # Evitar agregar el mismo alimento dos veces en la receta
        if any(i.food_id == food_id for i in self.ingredients_buffer):
            QMessageBox.warning(
                self,
                "Alimento Duplicado",
                "Este alimento ya está en la receta. Elimínelo de la lista si desea cambiar su cantidad.",
            )
            return

        food = self.food_service.get_food_by_id(food_id)
        if not food:
            return

        ing = RecipeIngredient(
            food_id=food.id,
            food_name=food.name,
            food_category=food.category,
            quantity=qty,
            unit=unit,
            food=food,
        )
        self.ingredients_buffer.append(ing)
        self._refresh_ingredients_table()
        self._recalculate_preview()

    def _refresh_ingredients_table(self):
        self.table_ingredients.setRowCount(len(self.ingredients_buffer))
        for row, ing in enumerate(self.ingredients_buffer):
            self.table_ingredients.setItem(row, 0, QTableWidgetItem(ing.food_name or f"Alimento #{ing.food_id}"))
            self.table_ingredients.setItem(row, 1, QTableWidgetItem(f"{ing.quantity:g}"))
            self.table_ingredients.setItem(row, 2, QTableWidgetItem(ing.unit))

            # Calcular costo aproximado
            cost = 0.0
            if ing.food:
                from src.services.nutrition_calc import calculate_ingredient_cost
                try:
                    cost = calculate_ingredient_cost(ing.food, ing.quantity, ing.unit)
                except Exception:
                    cost = 0.0
            self.table_ingredients.setItem(row, 3, QTableWidgetItem(f"S/. {cost:.2f}"))

            # Botón para quitar ingrediente — compacto y centrado
            btn_remove = QPushButton("✕ Quitar")
            btn_remove.setStyleSheet(
                "QPushButton {"
                "    background-color: #C53030;"
                "    color: #FFFFFF;"
                "    border: none;"
                "    border-radius: 3px;"
                "    padding: 2px 6px;"
                "    font-size: 11px;"
                "    font-weight: 600;"
                "}"
                "QPushButton:hover {"
                "    background-color: #9B2C2C;"
                "}"
            )
            btn_remove.setFixedHeight(23)
            btn_remove.setFixedWidth(72)
            btn_remove.setCursor(Qt.PointingHandCursor)
            btn_remove.clicked.connect(lambda checked, idx=row: self.on_remove_ingredient(idx))

            container = QWidget()
            c_layout = QHBoxLayout(container)
            c_layout.setContentsMargins(0, 0, 0, 0)
            c_layout.setAlignment(Qt.AlignCenter)
            c_layout.addWidget(btn_remove)
            self.table_ingredients.setCellWidget(row, 4, container)

    def on_remove_ingredient(self, row_idx: int):
        if 0 <= row_idx < len(self.ingredients_buffer):
            self.ingredients_buffer.pop(row_idx)
            self._refresh_ingredients_table()
            self._recalculate_preview()

    def _recalculate_preview(self):
        portions = self.input_portions.value()
        if portions <= 0 or not self.ingredients_buffer:
            self.lbl_preview_cost.setText("Costo Total: S/. 0.00")
            self.lbl_preview_portion_cost.setText("Costo por Porción: S/. 0.00")
            self.lbl_preview_calories.setText("Energía por Porción: 0.0 kcal")
            return

        temp_recipe = Recipe(
            name="Temp",
            base_portions=portions,
            ingredients=self.ingredients_buffer,
        )
        try:
            totals = calculate_recipe_totals(temp_recipe, target_portions=portions)
            self.lbl_preview_cost.setText(f"Costo Total: S/. {totals.total_cost:.2f}")
            self.lbl_preview_portion_cost.setText(f"Costo por Porción: S/. {totals.cost_per_portion:.2f}")
            cal = totals.nutrients_per_portion.get("calories")
            cal_str = f"{cal:.1f} kcal" if cal is not None else "No disp."
            self.lbl_preview_calories.setText(f"Energía por Porción: {cal_str}")
        except Exception:
            pass

    def load_recipe_data(self, recipe: Recipe):
        self.input_name.setText(recipe.name)
        self.input_desc.setText(recipe.description or "")
        self.input_portions.setValue(recipe.base_portions)
        self.ingredients_buffer = list(recipe.ingredients)
        self._refresh_ingredients_table()
        self._recalculate_preview()

    def get_recipe_object(self) -> Recipe:
        recipe_id = self.recipe.id if (self.is_edit and self.recipe) else None
        return Recipe(
            id=recipe_id,
            name=self.input_name.text().strip(),
            description=self.input_desc.text().strip() or None,
            base_portions=self.input_portions.value(),
            ingredients=self.ingredients_buffer,
        )


class RecipeDetailDialog(QDialog):
    """
    Diálogo para visualizar el detalle completo de una receta y realizar
    el escalado proporcional dinámico de porciones en tiempo real (T07).
    """

    def __init__(
        self,
        recipe_service: RecipeService,
        recipe_id: int,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.recipe_service = recipe_service
        self.recipe_id = recipe_id
        self.recipe = self.recipe_service.get_recipe_by_id(recipe_id)

        self.setWindowTitle(f"Detalle y Escalado — {self.recipe.name if self.recipe else 'Receta'}")
        self.resize(850, 680)
        self.init_ui()
        self.on_portions_changed()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        if not self.recipe:
            main_layout.addWidget(QLabel("No se encontró la información de la receta."))
            return

        # Encabezado con información general
        header_card = QFrame()
        header_card.setObjectName("cardFrame")
        h_layout = QVBoxLayout(header_card)

        lbl_name = QLabel(self.recipe.name)
        lbl_name.setStyleSheet("font-size: 18px; font-weight: 700; color: #1A365D;")
        h_layout.addWidget(lbl_name)

        if self.recipe.description:
            lbl_desc = QLabel(self.recipe.description)
            lbl_desc.setStyleSheet("color: #4A5568; font-style: italic;")
            h_layout.addWidget(lbl_desc)

        lbl_base = QLabel(f"Porciones base registradas: {self.recipe.base_portions}")
        lbl_base.setStyleSheet("color: #718096;")
        h_layout.addWidget(lbl_base)

        main_layout.addWidget(header_card)

        # Control interactivo de escalado
        scaling_bar = QHBoxLayout()
        scaling_bar.setSpacing(10)

        lbl_scale_title = QLabel("👥 Calcular requerimientos para:")
        lbl_scale_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #2B6CB0;")

        self.spin_target_portions = QSpinBox()
        self.spin_target_portions.setRange(1, 100000)
        self.spin_target_portions.setValue(self.recipe.base_portions)
        self.spin_target_portions.setSuffix(" comensales / porciones")
        self.spin_target_portions.setMinimumWidth(220)
        self.spin_target_portions.valueChanged.connect(self.on_portions_changed)

        self.btn_reset_portions = QPushButton("Restablecer a base")
        self.btn_reset_portions.setObjectName("btnSecondary")
        self.btn_reset_portions.clicked.connect(lambda: self.spin_target_portions.setValue(self.recipe.base_portions))

        scaling_bar.addWidget(lbl_scale_title)
        scaling_bar.addWidget(self.spin_target_portions)
        scaling_bar.addWidget(self.btn_reset_portions)
        scaling_bar.addStretch()

        main_layout.addLayout(scaling_bar)

        # Tarjetas de resumen de costos y energía
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(10)

        self.card_total_cost = self._create_metric_card("COSTO TOTAL", "S/. 0.00")
        self.card_portion_cost = self._create_metric_card("COSTO POR PORCIÓN", "S/. 0.00")
        self.card_portion_cal = self._create_metric_card("ENERGÍA POR PORCIÓN", "0 kcal")
        self.card_portion_prot = self._create_metric_card("PROTEÍNAS POR PORCIÓN", "0 g")

        metrics_layout.addWidget(self.card_total_cost)
        metrics_layout.addWidget(self.card_portion_cost)
        metrics_layout.addWidget(self.card_portion_cal)
        metrics_layout.addWidget(self.card_portion_prot)

        main_layout.addLayout(metrics_layout)

        # Tabla de insumos requeridos (víveres escalados)
        table_group = QGroupBox("Requerimiento de Víveres / Insumos Escalados")
        tg_layout = QVBoxLayout(table_group)

        self.table_ingredients = QTableWidget()
        self.table_ingredients.setColumnCount(5)
        self.table_ingredients.setHorizontalHeaderLabels([
            "Ingrediente",
            "Cant. Base",
            "Cant. Escalada Requerida",
            "Unidad",
            "Costo Insumo",
        ])
        self.table_ingredients.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_ingredients.horizontalHeader().setMinimumSectionSize(80)
        self.table_ingredients.verticalHeader().setVisible(False)
        self.table_ingredients.verticalHeader().setDefaultSectionSize(30)
        self.table_ingredients.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_ingredients.setAlternatingRowColors(True)
        tg_layout.addWidget(self.table_ingredients)

        main_layout.addWidget(table_group)

        # Tabla de desglose nutricional completo
        nutri_group = QGroupBox("Aporte Nutricional Completo")
        ng_layout = QVBoxLayout(nutri_group)

        self.table_nutrients = QTableWidget()
        self.table_nutrients.setColumnCount(4)
        self.table_nutrients.setHorizontalHeaderLabels([
            "Nutriente",
            "Unidad",
            "Aporte Total",
            "Aporte por Porción",
        ])
        self.table_nutrients.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_nutrients.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_nutrients.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_nutrients.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_nutrients.horizontalHeader().setMinimumSectionSize(100)
        self.table_nutrients.verticalHeader().setVisible(False)
        self.table_nutrients.verticalHeader().setDefaultSectionSize(28)
        self.table_nutrients.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_nutrients.setAlternatingRowColors(True)
        ng_layout.addWidget(self.table_nutrients)

        main_layout.addWidget(nutri_group)

        # Alertas o advertencias de datos incompletos
        self.lbl_warnings = QLabel("")
        self.lbl_warnings.setStyleSheet("color: #C53030; font-weight: 600;")
        self.lbl_warnings.setWordWrap(True)
        main_layout.addWidget(self.lbl_warnings)

        # Botón cerrar
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_close = QPushButton("Cerrar")
        self.btn_close.setObjectName("btnPrimary")
        self.btn_close.clicked.connect(self.accept)
        btn_box.addWidget(self.btn_close)
        main_layout.addLayout(btn_box)

    def _create_metric_card(self, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")
        l = QVBoxLayout(card)
        l.setContentsMargins(10, 8, 10, 8)
        l.setSpacing(4)
        lbl_t = QLabel(title)
        lbl_t.setObjectName("metricTitle")
        lbl_v = QLabel(value)
        lbl_v.setObjectName("metricValue")
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        card.lbl_val = lbl_v  # Guardar referencia
        return card

    def on_portions_changed(self):
        target = self.spin_target_portions.value()
        try:
            totals = self.recipe_service.calculate_recipe(self.recipe_id, target_portions=target)
        except Exception as e:
            QMessageBox.critical(self, "Error de Cálculo", f"Error al calcular receta:\n{str(e)}")
            return

        # Actualizar métricas
        self.card_total_cost.lbl_val.setText(f"S/. {totals.total_cost:.2f}")
        self.card_portion_cost.lbl_val.setText(f"S/. {totals.cost_per_portion:.2f}")

        cal_per = totals.nutrients_per_portion.get("calories")
        self.card_portion_cal.lbl_val.setText(f"{cal_per:.1f} kcal" if cal_per is not None else "—")

        prot_per = totals.nutrients_per_portion.get("protein")
        self.card_portion_prot.lbl_val.setText(f"{prot_per:.1f} g" if prot_per is not None else "—")

        # Actualizar tabla de insumos
        self.table_ingredients.setRowCount(len(totals.ingredients_detail))
        for r, detail in enumerate(totals.ingredients_detail):
            self.table_ingredients.setItem(r, 0, QTableWidgetItem(detail.food_name))
            self.table_ingredients.setItem(r, 1, QTableWidgetItem(f"{detail.original_quantity:g}"))
            self.table_ingredients.setItem(r, 2, QTableWidgetItem(f"{detail.scaled_quantity:g}"))
            self.table_ingredients.setItem(r, 3, QTableWidgetItem(detail.unit))
            self.table_ingredients.setItem(r, 4, QTableWidgetItem(f"S/. {detail.cost:.2f}"))

        # Actualizar tabla de nutrientes
        from src.services.nutrition_calc import NUTRIENT_FIELDS
        self.table_nutrients.setRowCount(len(NUTRIENT_FIELDS))
        for r, (key, label, u_label) in enumerate(NUTRIENT_FIELDS):
            t_val = totals.nutrients_total.get(key)
            p_val = totals.nutrients_per_portion.get(key)

            t_str = f"{t_val:.1f}" if t_val is not None else "No especificado"
            p_str = f"{p_val:.1f}" if p_val is not None else "No especificado"

            self.table_nutrients.setItem(r, 0, QTableWidgetItem(label))
            self.table_nutrients.setItem(r, 1, QTableWidgetItem(u_label))
            self.table_nutrients.setItem(r, 2, QTableWidgetItem(t_str))
            self.table_nutrients.setItem(r, 3, QTableWidgetItem(p_str))

        # Advertencias
        if totals.incomplete_nutrients_warnings:
            warn_text = "⚠️ Advertencias nutricionales:\n• " + "\n• ".join(totals.incomplete_nutrients_warnings[:4])
            if len(totals.incomplete_nutrients_warnings) > 4:
                warn_text += f"\n• ... y {len(totals.incomplete_nutrients_warnings) - 4} más."
            self.lbl_warnings.setText(warn_text)
        else:
            self.lbl_warnings.setText("")


class RecipeView(QWidget):
    """Pestaña principal de visualización y catálogo de recetas."""

    def __init__(
        self,
        food_service: FoodService,
        recipe_service: RecipeService,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.food_service = food_service
        self.recipe_service = recipe_service
        self.init_ui()
        self.refresh_recipes()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Barra superior de búsqueda y acciones
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 Buscar receta por nombre...")
        self.input_search.textChanged.connect(self.refresh_recipes)
        self.input_search.setMinimumWidth(260)

        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.setObjectName("btnSecondary")
        self.btn_clear.clicked.connect(self.input_search.clear)

        top_bar.addWidget(self.input_search)
        top_bar.addWidget(self.btn_clear)
        top_bar.addStretch()

        # Botones de acción
        self.btn_new = QPushButton("➕ Nueva Receta")
        self.btn_new.setObjectName("btnPrimary")
        self.btn_new.clicked.connect(self.on_new_recipe)

        self.btn_detail = QPushButton("📊 Ver Detalle y Escalado")
        self.btn_detail.setObjectName("btnSuccess")
        self.btn_detail.clicked.connect(self.on_view_detail)

        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setObjectName("btnSecondary")
        self.btn_edit.clicked.connect(self.on_edit_recipe)

        self.btn_duplicate = QPushButton("📋 Duplicar / Reutilizar")
        self.btn_duplicate.setObjectName("btnSecondary")
        self.btn_duplicate.clicked.connect(self.on_duplicate_recipe)

        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self.on_delete_recipe)

        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_detail)
        top_bar.addWidget(self.btn_edit)
        top_bar.addWidget(self.btn_duplicate)
        top_bar.addWidget(self.btn_delete)

        main_layout.addLayout(top_bar)

        # Tabla de recetas
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nombre de la Receta",
            "Porciones Base",
            "N° Ingredientes",
            "Costo Total Base",
            "Costo por Porción",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)
        rh = self.table.horizontalHeader()
        rh.setMinimumSectionSize(70)
        rh.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        rh.setSectionResizeMode(1, QHeaderView.Stretch)            # Nombre
        rh.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Porciones
        rh.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # N° Ing.
        rh.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Costo Total
        rh.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Costo Porc.
        rh.setStretchLastSection(False)
        self.table.doubleClicked.connect(self.on_view_detail)

        main_layout.addWidget(self.table)

        # Estado inferior
        self.lbl_status = QLabel("Listo.")
        main_layout.addWidget(self.lbl_status)

    def refresh_recipes(self):
        """Consulta y actualiza la lista de recetas calculando costos base."""
        search = self.input_search.text().strip()
        try:
            recipes = self.recipe_service.list_recipes(search=search)
            self.table.setRowCount(len(recipes))

            for row, rec in enumerate(recipes):
                self.table.setItem(row, 0, QTableWidgetItem(str(rec.id)))
                self.table.setItem(row, 1, QTableWidgetItem(rec.name))
                self.table.setItem(row, 2, QTableWidgetItem(str(rec.base_portions)))
                self.table.setItem(row, 3, QTableWidgetItem(str(len(rec.ingredients))))

                # Calcular costo total y costo por porción base
                try:
                    totals = self.recipe_service.calculate_recipe(rec.id)
                    cost_total_str = f"S/. {totals.total_cost:.2f}"
                    cost_portion_str = f"S/. {totals.cost_per_portion:.2f}"
                except Exception:
                    cost_total_str = "Error"
                    cost_portion_str = "Error"

                self.table.setItem(row, 4, QTableWidgetItem(cost_total_str))
                self.table.setItem(row, 5, QTableWidgetItem(cost_portion_str))

            self.lbl_status.setText(f"Mostrando {len(recipes)} receta(s) registrada(s).")
        except Exception as e:
            QMessageBox.critical(self, "Error al Cargar Recetas", f"Error inesperado:\n{str(e)}")

    def get_selected_recipe_id(self) -> Optional[int]:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def on_new_recipe(self):
        # Verificar si hay alimentos registrados en el catálogo
        foods = self.food_service.list_foods()
        if not foods:
            QMessageBox.information(
                self,
                "Catálogo Vacío",
                "Para crear una receta, primero debe registrar al menos un alimento en el Catálogo de Alimentos.",
            )
            return

        dialog = RecipeFormDialog(self.food_service, self.recipe_service, self)
        if dialog.exec() == QDialog.Accepted:
            new_recipe = dialog.get_recipe_object()
            try:
                self.recipe_service.add_recipe(new_recipe)
                self.refresh_recipes()
                QMessageBox.information(
                    self, "Receta Creada", f"La receta '{new_recipe.name}' fue registrada exitosamente."
                )
            except DuplicateRecipeError as e:
                QMessageBox.warning(self, "Receta Duplicada", str(e))
            except RecipeValidationError as e:
                QMessageBox.warning(self, "Validación Fallida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", f"Error inesperado:\n{str(e)}")

    def on_edit_recipe(self):
        recipe_id = self.get_selected_recipe_id()
        if recipe_id is None:
            QMessageBox.information(self, "Seleccionar Receta", "Por favor seleccione una receta de la lista para editar.")
            return

        recipe = self.recipe_service.get_recipe_by_id(recipe_id)
        if not recipe:
            QMessageBox.warning(self, "No Encontrada", "La receta seleccionada no se encontró en la base de datos.")
            return

        dialog = RecipeFormDialog(self.food_service, self.recipe_service, self, recipe=recipe)
        if dialog.exec() == QDialog.Accepted:
            updated_recipe = dialog.get_recipe_object()
            try:
                self.recipe_service.update_recipe(updated_recipe)
                self.refresh_recipes()
                QMessageBox.information(
                    self, "Receta Actualizada", f"La receta '{updated_recipe.name}' se actualizó exitosamente."
                )
            except DuplicateRecipeError as e:
                QMessageBox.warning(self, "Nombre Duplicado", str(e))
            except RecipeValidationError as e:
                QMessageBox.warning(self, "Validación Fallida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error al Actualizar", f"Error inesperado:\n{str(e)}")

    def on_view_detail(self):
        recipe_id = self.get_selected_recipe_id()
        if recipe_id is None:
            QMessageBox.information(self, "Seleccionar Receta", "Por favor seleccione una receta de la lista para ver su detalle y escalado.")
            return

        dialog = RecipeDetailDialog(self.recipe_service, recipe_id, self)
        dialog.exec()

    def on_duplicate_recipe(self):
        recipe_id = self.get_selected_recipe_id()
        if recipe_id is None:
            QMessageBox.information(self, "Seleccionar Receta", "Por favor seleccione una receta de la lista para duplicarla.")
            return

        try:
            cloned = self.recipe_service.duplicate_recipe(recipe_id)
            self.refresh_recipes()
            QMessageBox.information(
                self,
                "Receta Duplicada",
                f"Se creó una nueva receta '{cloned.name}'. Ahora puede editarla libremente.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al Duplicar", f"Error al duplicar receta:\n{str(e)}")

    def on_delete_recipe(self):
        recipe_id = self.get_selected_recipe_id()
        if recipe_id is None:
            QMessageBox.information(self, "Seleccionar Receta", "Por favor seleccione una receta de la lista para eliminar.")
            return

        recipe = self.recipe_service.get_recipe_by_id(recipe_id)
        if not recipe:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar la receta '{recipe.name}'?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            try:
                self.recipe_service.delete_recipe(recipe_id)
                self.refresh_recipes()
                QMessageBox.information(self, "Eliminada", f"La receta '{recipe.name}' fue eliminada exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error al Eliminar", f"Error inesperado:\n{str(e)}")

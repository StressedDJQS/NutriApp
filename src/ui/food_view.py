"""
Vista del catálogo y formulario de alimentos (HU-01, T02, T03, T04).
Permite registrar, buscar, filtrar, editar y eliminar alimentos con validación en español.
"""

from typing import Optional, Callable
from PySide6.QtCore import Qt, Signal
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
    QDoubleSpinBox,
    QGroupBox,
    QSplitter,
    QFrame,
)

from src.models.food import Food
from src.services.food_service import (
    FoodService,
    FoodValidationError,
    DuplicateFoodError,
    FoodInUseError,
)


class FoodFormDialog(QDialog):
    """Diálogo modal para el registro y edición de alimentos."""

    def __init__(self, parent: Optional[QWidget] = None, food: Optional[Food] = None):
        super().__init__(parent)
        self.food = food
        self.is_edit = food is not None
        self.setWindowTitle("Editar Alimento" if self.is_edit else "Registrar Nuevo Alimento")
        self.setMinimumWidth(520)
        self.init_ui()

        if self.is_edit and self.food:
            self.load_food_data(self.food)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Grupo: Información General
        gen_group = QGroupBox("Datos Básicos")
        gen_layout = QFormLayout(gen_group)
        gen_layout.setSpacing(8)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: Arroz blanco de mesa, Pechuga de pollo...")

        self.input_category = QComboBox()
        self.input_category.setEditable(True)
        common_categories = [
            "Cereales y derivados",
            "Carnes, aves y pescados",
            "Lácteos y derivados",
            "Verduras y hortalizas",
            "Frutas",
            "Legumbres y menestras",
            "Grasas y aceites",
            "Huevos",
            "Azúcares y dulces",
            "Condimentos y especias",
        ]
        self.input_category.addItems(common_categories)

        # Unidad física y precio
        self.input_unit = QComboBox()
        self.input_unit.addItems(["g", "kg", "ml", "l", "unidad"])
        self.input_unit.currentTextChanged.connect(self._on_unit_changed)

        self.input_price = QDoubleSpinBox()
        self.input_price.setRange(0.0, 999999.0)
        self.input_price.setDecimals(2)
        self.input_price.setPrefix("S/. ")

        self.input_price_unit = QComboBox()
        self.input_price_unit.addItems(["kg", "g", "l", "ml", "unidad"])

        price_row = QHBoxLayout()
        price_row.addWidget(self.input_price)
        price_row.addWidget(QLabel("por"))
        price_row.addWidget(self.input_price_unit)

        gen_layout.addRow("Nombre del alimento (*):", self.input_name)
        gen_layout.addRow("Categoría:", self.input_category)
        gen_layout.addRow("Unidad de medida física (*):", self.input_unit)
        gen_layout.addRow("Precio unitario de compra (*):", price_row)

        layout.addWidget(gen_group)

        # Grupo: Perfil Nutricional
        nutri_group = QGroupBox("Aporte Nutricional (por cada 100 g / 100 ml / 1 unidad)")
        nutri_layout = QFormLayout(nutri_group)
        nutri_layout.setSpacing(8)

        self.input_calories = QDoubleSpinBox()
        self.input_calories.setRange(0.0, 9999.0)
        self.input_calories.setDecimals(1)
        self.input_calories.setSpecialValueText("No especificado")
        self.input_calories.setValue(0.0)

        self.input_protein = QDoubleSpinBox()
        self.input_protein.setRange(0.0, 999.0)
        self.input_protein.setDecimals(1)
        self.input_protein.setSpecialValueText("No especificado")
        self.input_protein.setValue(0.0)

        self.input_carbs = QDoubleSpinBox()
        self.input_carbs.setRange(0.0, 999.0)
        self.input_carbs.setDecimals(1)
        self.input_carbs.setSpecialValueText("No especificado")
        self.input_carbs.setValue(0.0)

        self.input_fats = QDoubleSpinBox()
        self.input_fats.setRange(0.0, 999.0)
        self.input_fats.setDecimals(1)
        self.input_fats.setSpecialValueText("No especificado")
        self.input_fats.setValue(0.0)

        self.input_fiber = QDoubleSpinBox()
        self.input_fiber.setRange(0.0, 999.0)
        self.input_fiber.setDecimals(1)
        self.input_fiber.setSpecialValueText("No especificado")
        self.input_fiber.setValue(0.0)

        self.input_sodium = QDoubleSpinBox()
        self.input_sodium.setRange(0.0, 99999.0)
        self.input_sodium.setDecimals(1)
        self.input_sodium.setSpecialValueText("No especificado")
        self.input_sodium.setValue(0.0)

        nutri_layout.addRow("Energía (kcal):", self.input_calories)
        nutri_layout.addRow("Proteínas (g):", self.input_protein)
        nutri_layout.addRow("Carbohidratos (g):", self.input_carbs)
        nutri_layout.addRow("Grasas totales (g):", self.input_fats)
        nutri_layout.addRow("Fibra dietética (g):", self.input_fiber)
        nutri_layout.addRow("Sodio (mg):", self.input_sodium)

        layout.addWidget(nutri_group)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("btnSecondary")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Guardar Alimento")
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def _on_unit_changed(self, text: str):
        """Sincroniza la unidad de precio sugerida según la unidad física seleccionada."""
        u = text.strip().lower()
        if u in ("g", "kg"):
            self.input_price_unit.setCurrentText("kg")
        elif u in ("ml", "l"):
            self.input_price_unit.setCurrentText("l")
        elif u == "unidad":
            self.input_price_unit.setCurrentText("unidad")

    def load_food_data(self, food: Food):
        self.input_name.setText(food.name)
        if food.category:
            self.input_category.setCurrentText(food.category)
        self.input_unit.setCurrentText(food.unit)
        self.input_price.setValue(food.unit_price)
        self.input_price_unit.setCurrentText(food.price_unit)

        if food.calories is not None:
            self.input_calories.setValue(food.calories)
        if food.protein is not None:
            self.input_protein.setValue(food.protein)
        if food.carbohydrates is not None:
            self.input_carbs.setValue(food.carbohydrates)
        if food.fats is not None:
            self.input_fats.setValue(food.fats)
        if food.fiber is not None:
            self.input_fiber.setValue(food.fiber)
        if food.sodium is not None:
            self.input_sodium.setValue(food.sodium)

    def get_food_object(self) -> Food:
        """Construye y retorna una instancia de Food a partir de los datos ingresados."""
        unit = self.input_unit.currentText().strip()
        ref_base_amount = 1.0 if unit == "unidad" else 100.0
        ref_base_unit = "unidad" if unit == "unidad" else ("ml" if unit in ("ml", "l") else "g")

        cal = self.input_calories.value() if self.input_calories.value() > 0 or self.input_calories.text() != "No especificado" else None
        prot = self.input_protein.value() if self.input_protein.value() > 0 or self.input_protein.text() != "No especificado" else None
        carbs = self.input_carbs.value() if self.input_carbs.value() > 0 or self.input_carbs.text() != "No especificado" else None
        fats = self.input_fats.value() if self.input_fats.value() > 0 or self.input_fats.text() != "No especificado" else None
        fiber = self.input_fiber.value() if self.input_fiber.value() > 0 or self.input_fiber.text() != "No especificado" else None
        sod = self.input_sodium.value() if self.input_sodium.value() > 0 or self.input_sodium.text() != "No especificado" else None

        food_id = self.food.id if (self.is_edit and self.food) else None

        return Food(
            id=food_id,
            name=self.input_name.text().strip(),
            category=self.input_category.currentText().strip() or None,
            unit=unit,
            reference_base_amount=ref_base_amount,
            reference_base_unit=ref_base_unit,
            unit_price=self.input_price.value(),
            price_unit=self.input_price_unit.currentText().strip(),
            calories=cal,
            protein=prot,
            carbohydrates=carbs,
            fats=fats,
            fiber=fiber,
            sodium=sod,
        )


class FoodView(QWidget):
    """Pestaña principal de visualización y catálogo de alimentos."""

    # Señal emitida cuando el catálogo de alimentos cambia (para actualizar recetas)
    foods_changed = Signal()

    def __init__(self, food_service: FoodService, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.food_service = food_service
        self.init_ui()
        self.refresh_foods()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Barra superior de filtros y acciones
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 Buscar alimento por nombre...")
        self.input_search.textChanged.connect(self.refresh_foods)
        self.input_search.setMinimumWidth(260)

        self.combo_filter_category = QComboBox()
        self.combo_filter_category.addItem("Todas las categorías")
        self.combo_filter_category.currentTextChanged.connect(self.refresh_foods)
        self.combo_filter_category.setMinimumWidth(180)

        self.btn_clear_filters = QPushButton("Limpiar")
        self.btn_clear_filters.setObjectName("btnSecondary")
        self.btn_clear_filters.clicked.connect(self.clear_filters)

        top_bar.addWidget(self.input_search)
        top_bar.addWidget(QLabel("Categoría:"))
        top_bar.addWidget(self.combo_filter_category)
        top_bar.addWidget(self.btn_clear_filters)
        top_bar.addStretch()

        # Botones principales de acción
        self.btn_new = QPushButton("➕ Nuevo Alimento")
        self.btn_new.setObjectName("btnPrimary")
        self.btn_new.clicked.connect(self.on_add_food)

        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setObjectName("btnSecondary")
        self.btn_edit.clicked.connect(self.on_edit_food)

        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self.on_delete_food)

        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_edit)
        top_bar.addWidget(self.btn_delete)

        main_layout.addLayout(top_bar)

        # Tabla de alimentos
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Alimento",
            "Categoría",
            "Unidad",
            "Precio Ref.",
            "Energía (kcal)",
            "Proteínas (g)",
            "Carbohidratos (g)",
            "Grasas (g)",
            "Fibra (g)",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)
        hh = self.table.horizontalHeader()
        hh.setMinimumSectionSize(60)
        hh.setDefaultSectionSize(110)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # ID
        hh.setSectionResizeMode(1, QHeaderView.Stretch)             # Alimento
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)    # Categoría
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)    # Unidad
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)    # Precio
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)    # Energía
        hh.setSectionResizeMode(6, QHeaderView.ResizeToContents)    # Proteínas
        hh.setSectionResizeMode(7, QHeaderView.ResizeToContents)    # Carbohidratos
        hh.setSectionResizeMode(8, QHeaderView.ResizeToContents)    # Grasas
        hh.setSectionResizeMode(9, QHeaderView.ResizeToContents)    # Fibra
        hh.setStretchLastSection(False)
        self.table.doubleClicked.connect(self.on_edit_food)

        main_layout.addWidget(self.table)

        # Estado inferior
        self.lbl_status = QLabel("Listo.")
        main_layout.addWidget(self.lbl_status)

    def clear_filters(self):
        self.input_search.clear()
        self.combo_filter_category.setCurrentIndex(0)
        self.refresh_foods()

    def refresh_categories(self):
        """Actualiza el combo de categorías con las presentes en la BD sin perder selección."""
        current = self.combo_filter_category.currentText()
        categories = self.food_service.get_categories()
        self.combo_filter_category.blockSignals(True)
        self.combo_filter_category.clear()
        self.combo_filter_category.addItem("Todas las categorías")
        for cat in categories:
            self.combo_filter_category.addItem(cat)

        index = self.combo_filter_category.findText(current)
        if index >= 0:
            self.combo_filter_category.setCurrentIndex(index)
        else:
            self.combo_filter_category.setCurrentIndex(0)
        self.combo_filter_category.blockSignals(False)

    def refresh_foods(self):
        """Consulta y actualiza la tabla de alimentos."""
        search = self.input_search.text().strip()
        cat = self.combo_filter_category.currentText()
        selected_cat = None if cat == "Todas las categorías" else cat

        try:
            foods = self.food_service.list_foods(search=search, category=selected_cat)
            self.refresh_categories()

            self.table.setRowCount(len(foods))
            for row, food in enumerate(foods):
                self.table.setItem(row, 0, QTableWidgetItem(str(food.id)))
                self.table.setItem(row, 1, QTableWidgetItem(food.name))
                self.table.setItem(row, 2, QTableWidgetItem(food.category or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(food.unit))

                price_text = f"S/. {food.unit_price:.2f} / {food.price_unit}"
                self.table.setItem(row, 4, QTableWidgetItem(price_text))

                cal_text = f"{food.calories:.1f}" if food.calories is not None else "—"
                prot_text = f"{food.protein:.1f}" if food.protein is not None else "—"
                carbs_text = f"{food.carbohydrates:.1f}" if food.carbohydrates is not None else "—"
                fats_text = f"{food.fats:.1f}" if food.fats is not None else "—"
                fiber_text = f"{food.fiber:.1f}" if food.fiber is not None else "—"

                self.table.setItem(row, 5, QTableWidgetItem(cal_text))
                self.table.setItem(row, 6, QTableWidgetItem(prot_text))
                self.table.setItem(row, 7, QTableWidgetItem(carbs_text))
                self.table.setItem(row, 8, QTableWidgetItem(fats_text))
                self.table.setItem(row, 9, QTableWidgetItem(fiber_text))

            total = len(foods)
            self.lbl_status.setText(f"Mostrando {total} alimento(s) registrado(s).")
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar alimentos", f"Ocurrió un error inesperado:\n{str(e)}")

    def get_selected_food_id(self) -> Optional[int]:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def on_add_food(self):
        dialog = FoodFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_food = dialog.get_food_object()
            try:
                self.food_service.add_food(new_food)
                self.refresh_foods()
                self.foods_changed.emit()
                QMessageBox.information(
                    self, "Alimento Registrado", f"El alimento '{new_food.name}' fue registrado exitosamente."
                )
            except DuplicateFoodError as e:
                QMessageBox.warning(self, "Alimento Duplicado", str(e))
            except FoodValidationError as e:
                QMessageBox.warning(self, "Validación Fallida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", f"Error no esperado:\n{str(e)}")

    def on_edit_food(self):
        food_id = self.get_selected_food_id()
        if food_id is None:
            QMessageBox.information(self, "Seleccionar Alimento", "Por favor seleccione un alimento de la lista para editar.")
            return

        food = self.food_service.get_food_by_id(food_id)
        if food is None:
            QMessageBox.warning(self, "No Encontrado", "El alimento seleccionado no se encontró en la base de datos.")
            return

        dialog = FoodFormDialog(self, food=food)
        if dialog.exec() == QDialog.Accepted:
            updated_food = dialog.get_food_object()
            try:
                self.food_service.update_food(updated_food)
                self.refresh_foods()
                self.foods_changed.emit()
                QMessageBox.information(
                    self, "Alimento Actualizado", f"El alimento '{updated_food.name}' se actualizó correctamente."
                )
            except DuplicateFoodError as e:
                QMessageBox.warning(self, "Nombre Duplicado", str(e))
            except FoodValidationError as e:
                QMessageBox.warning(self, "Validación Fallida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error al Actualizar", f"Error no esperado:\n{str(e)}")

    def on_delete_food(self):
        food_id = self.get_selected_food_id()
        if food_id is None:
            QMessageBox.information(self, "Seleccionar Alimento", "Por favor seleccione un alimento de la lista para eliminar.")
            return

        food = self.food_service.get_food_by_id(food_id)
        if food is None:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el alimento '{food.name}'?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            try:
                self.food_service.delete_food(food_id)
                self.refresh_foods()
                self.foods_changed.emit()
                QMessageBox.information(self, "Eliminado", f"El alimento '{food.name}' fue eliminado exitosamente.")
            except FoodInUseError as e:
                QMessageBox.warning(self, "Operación Bloqueada", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error al Eliminar", f"Error no esperado:\n{str(e)}")

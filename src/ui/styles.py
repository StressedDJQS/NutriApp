"""
Estilos visuales QSS para NutriApp.
Corregido: se eliminó la asignación de background-color en QWidget global
para evitar que sobreescriba contenedores con fondo oscuro (headerFrame)
y encabezados de tablas (QHeaderView).
"""

APP_STYLE = """
/* Base — solo tipografía y color de texto; NO background global para no sobreescribir
   contenedores con fondo oscuro ni encabezados de tablas */
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #2D3748;
}

/* Fondo claro de la ventana principal y diálogos */
QMainWindow, QDialog {
    background-color: #F7FAFC;
}

/* Encabezado institucional */
QFrame#headerFrame {
    background-color: #1A365D;
    border-bottom: 2px solid #2B6CB0;
}

/* Las etiquetas dentro del header NO deben heredar background blanco */
QFrame#headerFrame QLabel {
    background-color: transparent;
}

QLabel#appTitle {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
    background-color: transparent;
}

QLabel#appSubtitle {
    color: #E2E8F0;
    font-size: 12px;
    background-color: transparent;
}

/* Contenido principal */
QWidget#centralWidget, QTabWidget > QWidget {
    background-color: #F7FAFC;
}

/* Pestañas de navegación principal */
QTabWidget::pane {
    border: 1px solid #CBD5E0;
    background: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background: #EDF2F7;
    color: #4A5568;
    padding: 10px 24px;
    margin-right: 4px;
    font-weight: 600;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #CBD5E0;
    border-bottom: none;
    min-width: 160px;
}

QTabBar::tab:selected {
    background: #FFFFFF;
    color: #2B6CB0;
    border-top: 2px solid #2B6CB0;
}

QTabBar::tab:hover:!selected {
    background: #E2E8F0;
    color: #2D3748;
}

/* Tarjetas y contenedores */
QFrame#cardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 14px;
}

QGroupBox {
    font-weight: 600;
    color: #2C5282;
    border: 1px solid #CBD5E0;
    border-radius: 6px;
    margin-top: 16px;
    padding-top: 16px;
    background: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 0px;
    padding: 0 6px;
    background-color: #FFFFFF;
    color: #2C5282;
}

/* Entradas de texto y controles */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E0;
    border-radius: 5px;
    padding: 6px 10px;
    color: #2D3748;
    min-height: 22px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #3182CE;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #CBD5E0;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #2D3748;
    selection-background-color: #EBF8FF;
    selection-color: #2B6CB0;
    border: 1px solid #CBD5E0;
}

/* Tablas — encabezados con alto contraste explícito */
QTableWidget {
    background-color: #FFFFFF;
    color: #2D3748;
    border: 1px solid #CBD5E0;
    gridline-color: #EDF2F7;
    selection-background-color: #EBF8FF;
    selection-color: #2B6CB0;
    alternate-background-color: #F8FAFC;
}

/* CRÍTICO: QHeaderView debe tener sus propios color y background explícitos.
   Sin esto, hereda el color de QWidget y los encabezados pueden quedar invisibles. */
QHeaderView {
    background-color: #F1F5F9;
}

QHeaderView::section {
    background-color: #E8EEF6;
    color: #1A365D;
    font-weight: 700;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #CBD5E1;
    border-bottom: 2px solid #A0AEC0;
}

QHeaderView::section:first {
    border-left: none;
}

QHeaderView::section:last {
    border-right: none;
}

QTableWidget::item {
    padding: 6px 8px;
    color: #2D3748;
    border-bottom: 1px solid #F1F5F9;
}

QTableWidget::item:selected {
    background-color: #EBF8FF;
    color: #2B6CB0;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #F1F5F9;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #CBD5E0;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Botones */
QPushButton {
    background-color: #EDF2F7;
    color: #2D3748;
    border: 1px solid #CBD5E0;
    border-radius: 5px;
    padding: 7px 16px;
    font-weight: 600;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #E2E8F0;
    border-color: #A0AEC0;
}

QPushButton:pressed {
    background-color: #CBD5E0;
}

QPushButton#btnPrimary {
    background-color: #2B6CB0;
    color: #FFFFFF;
    border: 1px solid #2B6CB0;
}

QPushButton#btnPrimary:hover {
    background-color: #2C5282;
    border-color: #2C5282;
}

QPushButton#btnSuccess {
    background-color: #2F855A;
    color: #FFFFFF;
    border: 1px solid #2F855A;
}

QPushButton#btnSuccess:hover {
    background-color: #276749;
}

QPushButton#btnDanger {
    background-color: #C53030;
    color: #FFFFFF;
    border: 1px solid #C53030;
}

QPushButton#btnDanger:hover {
    background-color: #9B2C2C;
}

QPushButton#btnSecondary {
    background-color: #EDF2F7;
    color: #4A5568;
    border: 1px solid #CBD5E0;
}

/* Tarjetas de métricas */
QFrame#metricCard {
    background-color: #F0F5FF;
    border: 1px solid #BEE3F8;
    border-radius: 6px;
    padding: 10px;
}

QLabel#metricTitle {
    font-size: 10px;
    font-weight: 700;
    color: #4A5568;
    background-color: transparent;
}

QLabel#metricValue {
    font-size: 17px;
    font-weight: 700;
    color: #1A365D;
    background-color: transparent;
}

/* Barra de estado */
QStatusBar {
    background-color: #EDF2F7;
    color: #4A5568;
    border-top: 1px solid #CBD5E0;
}

QStatusBar QLabel {
    background-color: transparent;
    color: #4A5568;
}

/* Labels genéricos: sin fondo por defecto para no tapar contenedores coloreados */
QLabel {
    background-color: transparent;
}

/* Diálogos y ventanas de formulario */
QDialog QWidget {
    background-color: #FFFFFF;
}

QDialog QLabel {
    background-color: transparent;
    color: #2D3748;
}

QFormLayout > QLabel {
    color: #4A5568;
    font-weight: 600;
}

/* Asegurar contraste de QSpinBox y QDoubleSpinBox en diálogos */
QDialog QSpinBox, QDialog QDoubleSpinBox, QDialog QLineEdit, QDialog QComboBox {
    background-color: #FFFFFF;
    color: #2D3748;
    border: 1px solid #CBD5E0;
}
"""

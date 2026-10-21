"""
Gestor de conexiones SQLite para NutriApp.
Garantiza persistencia real, activación obligatoria de claves foráneas y consultas parametrizadas.
"""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
from typing import Generator, Optional

from src.database.schema import SCHEMA_SQL


def get_default_db_path() -> Path:
    """Retorna la ruta por defecto persistente de la base de datos local."""
    # Obtenemos la raíz del proyecto (directorio que contiene src/)
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "nutriapp.db"


class Database:
    def __init__(self, db_path: Optional[str | Path] = None):
        if db_path is None:
            self.db_path = get_default_db_path()
        else:
            self.db_path = Path(db_path)
            if self.db_path != Path(":memory:"):
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Crea y retorna una nueva conexión SQLite con foreign keys activadas."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=15.0,
        )
        conn.row_factory = sqlite3.Row
        # Activar siempre claves foráneas
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager para gestionar automáticamente commit y rollback de transacciones."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_schema(self) -> None:
        """Inicializa las tablas e índices si no existen, sin alterar datos existentes."""
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)


# Instancia singleton por defecto para la aplicación
_default_db: Optional[Database] = None


def get_database(db_path: Optional[str | Path] = None) -> Database:
    """Retorna la instancia global o crea una nueva con la ruta especificada."""
    global _default_db
    if db_path is not None:
        return Database(db_path)
    if _default_db is None:
        _default_db = Database()
    return _default_db

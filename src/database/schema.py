"""
Definición del esquema DDL de la base de datos SQLite para NutriApp.
Cumple con T01 y T05: modelo normalizado con claves foráneas e integridad referencial.
"""

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    unit TEXT NOT NULL,
    reference_base_amount REAL NOT NULL DEFAULT 100.0 CHECK(reference_base_amount > 0),
    reference_base_unit TEXT NOT NULL DEFAULT 'g',
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    price_unit TEXT NOT NULL,
    calories REAL CHECK(calories IS NULL OR calories >= 0),
    protein REAL CHECK(protein IS NULL OR protein >= 0),
    carbohydrates REAL CHECK(carbohydrates IS NULL OR carbohydrates >= 0),
    fats REAL CHECK(fats IS NULL OR fats >= 0),
    fiber REAL CHECK(fiber IS NULL OR fiber >= 0),
    sodium REAL CHECK(sodium IS NULL OR sodium >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_foods_name_nocase ON foods(TRIM(name) COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_foods_category ON foods(category);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    base_portions INTEGER NOT NULL CHECK(base_portions > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_name_nocase ON recipes(TRIM(name) COLLATE NOCASE);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK(quantity > 0),
    unit TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_food ON recipe_ingredients(food_id);
"""

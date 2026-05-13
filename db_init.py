import sqlite3

DB_NAME = "asociacion.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Tabla de socios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dni TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            activo INTEGER DEFAULT 1
        );
    """)

    # Tabla de pagos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            concepto TEXT NOT NULL,
            importe REAL NOT NULL,
            metodo_pago TEXT,
            FOREIGN KEY (socio_id) REFERENCES socios(id)
        );
    """)

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    init_db()

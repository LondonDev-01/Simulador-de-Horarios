import sqlite3
import hashlib
import os
from typing import Optional, Dict, Tuple

class AuthManager:
    """
    Gestor de autenticación y licencias con persistencia en SQLite.
    Diseñado para ser compatible con PostgreSQL (Neon.tech / Supabase).
    """
    
    def __init__(self, db_path: str = "usuarios.db"):
        self.db_path = db_path
        self.is_authenticated = False
        self.current_user: Optional[str] = None
        self._init_db()

    def _init_db(self):
        """Inicializa la tabla de usuarios si no existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    def _hash_password(self, password: str) -> str:
        """Genera un hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """Registra un nuevo usuario (inactivo por defecto)"""
        if not username or not password:
            return False, "Usuario y contraseña son requeridos."
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash, is_active) VALUES (?, ?, ?)",
                (username, self._hash_password(password), 0)
            )
            conn.commit()
            conn.close()
            return True, "Registro exitoso. Tu cuenta está pendiente de activación."
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe."
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Valida credenciales y verifica si la cuenta está activa"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash, is_active FROM usuarios WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                return False, "Usuario no encontrado."

            db_hash, is_active = result
            if db_hash != self._hash_password(password):
                return False, "Contraseña incorrecta."

            if not is_active:
                return False, f"Cuenta '{username}' pendiente de activación. Contacta al admin."

            self.is_authenticated = True
            self.current_user = username
            return True, "Acceso concedido."

        except Exception as e:
            return False, f"Error en login: {str(e)}"

    def logout(self):
        self.is_authenticated = False
        self.current_user = None

    def has_active_license(self) -> bool:
        """Verificación rápida de seguridad"""
        return self.is_authenticated

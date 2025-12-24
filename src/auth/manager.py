from typing import Optional, Dict

class AuthManager:
    """
    Gestor de autenticación y licencias.
    Preparado para integración con PostgreSQL (Neon.tech / Supabase).
    """
    
    def __init__(self):
        self.is_authenticated = False
        self.current_user: Optional[Dict] = None

    def login(self, username: str, password: str) -> bool:
        """
        Lógica de login. 
        TODO: Conectar con base de datos remota para validación real.
        """
        # Placeholder para desarrollo: admite cualquier usuario con password '123'
        if password == "123":
            self.is_authenticated = True
            self.current_user = {"username": username, "tier": "premium"}
            return True
        return False

    def logout(self):
        self.is_authenticated = False
        self.current_user = None

    def has_active_license(self) -> bool:
        """Verifica si el usuario tiene permiso para generar horarios."""
        if not self.is_authenticated:
            return False
        # Aquí se validaría la fecha de expiración contra la DB
        return True

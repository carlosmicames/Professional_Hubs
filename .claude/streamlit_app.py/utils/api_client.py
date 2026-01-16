"""
API Client for Professional Hubs Backend.
Handles all communication with the FastAPI server.
Updated with firm settings endpoints.
"""

import os
import requests
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()


class ProfessionalHubsAPI:
    """Client for Professional Hubs API."""

    def __init__(self, base_url: Optional[str] = None, firm_id: int = 1):
        """
        Initialize API client.

        Args:
            base_url: API base URL (defaults to env var or localhost)
            firm_id: Law firm ID for multi-tenant isolation (MVP: always 1)
        """
        self.base_url = base_url or os.getenv(
            "LEXOS_API_BASE_URL",
            os.getenv("API_BASE_URL", "https://web-professional-hubs.up.railway.app")
        )
        self.api_version = "v1"
        self.firm_id = firm_id
        self.timeout = 30

    @property
    def _headers(self) -> Dict[str, str]:
        """Default headers including firm ID."""
        return {
            "Content-Type": "application/json",
            "X-Firm-ID": str(self.firm_id)
        }

    @property
    def _base_api_url(self) -> str:
        """Full API base URL with version."""
        return f"{self.base_url}/api/{self.api_version}"

    def _handle_error(self, e: Exception, context: str = "") -> Dict[str, Any]:
        """Handle API errors consistently."""
        if isinstance(e, requests.exceptions.HTTPError):
            error_detail = "Error desconocido"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            return {"success": False, "error": error_detail}
        return {"success": False, "error": f"Error de conexion: {str(e)}"}

    # =========================================================================
    # HEALTH & STATUS
    # =========================================================================

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    # =========================================================================
    # FIRMA (Company Settings)
    # =========================================================================

    def get_firma(self) -> Dict[str, Any]:
        """Get firm settings."""
        try:
            response = requests.get(
                f"{self._base_api_url}/firmas/{self.firm_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            return {"success": True, "data": None}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def update_firma(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update/create firm settings (upsert)."""
        try:
            response = requests.put(
                f"{self._base_api_url}/firmas/{self.firm_id}",
                json=data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # PERFIL (Profile)
    # =========================================================================

    def get_perfil(self) -> Dict[str, Any]:
        """Get profile settings."""
        try:
            response = requests.get(
                f"{self._base_api_url}/perfil/{self.firm_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            return {"success": True, "data": None}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def update_perfil(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update/create profile settings (upsert)."""
        try:
            response = requests.put(
                f"{self._base_api_url}/perfil/{self.firm_id}",
                json=data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # ESTUDIOS (Education)
    # =========================================================================

    def get_estudios(self) -> Dict[str, Any]:
        """Get education settings."""
        try:
            response = requests.get(
                f"{self._base_api_url}/estudios/{self.firm_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            return {"success": True, "data": None}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def update_estudios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update/create education settings (upsert)."""
        try:
            response = requests.put(
                f"{self._base_api_url}/estudios/{self.firm_id}",
                json=data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # AREAS DE PRACTICA (Practice Areas)
    # =========================================================================

    def get_areas_practica(self) -> Dict[str, Any]:
        """Get practice areas settings."""
        try:
            response = requests.get(
                f"{self._base_api_url}/areas-practica/{self.firm_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            return {"success": True, "data": None}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def update_areas_practica(self, areas: List[str]) -> Dict[str, Any]:
        """Update/create practice areas (upsert)."""
        try:
            response = requests.put(
                f"{self._base_api_url}/areas-practica/{self.firm_id}",
                json={"areas": areas},
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # UBICACION (Geographic Location)
    # =========================================================================

    def get_ubicacion(self) -> Dict[str, Any]:
        """Get location settings."""
        try:
            response = requests.get(
                f"{self._base_api_url}/ubicacion/{self.firm_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            return {"success": True, "data": None}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def update_ubicacion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update/create location settings (upsert)."""
        try:
            response = requests.put(
                f"{self._base_api_url}/ubicacion/{self.firm_id}",
                json=data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # PLANES (Subscription Plans)
    # =========================================================================

    def get_planes(self) -> Dict[str, Any]:
        """Get subscription plan settings."""
        try:
            response = requests.get(
                f"{self._base_api_url}/planes/{self.firm_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            return {"success": True, "data": None}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def update_planes(self, selected_plan: str) -> Dict[str, Any]:
        """Update/create subscription plan (upsert)."""
        try:
            payload = {"selected_plan": selected_plan}
            if selected_plan == "Basico":
                payload["trial_days"] = 14
            response = requests.put(
                f"{self._base_api_url}/planes/{self.firm_id}",
                json=payload,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # UPLOADS (Logo, Signature)
    # =========================================================================

    def upload_logo(self, file) -> Dict[str, Any]:
        """Upload company logo."""
        try:
            files = {"file": file}
            headers = {"X-Firm-ID": str(self.firm_id)}
            response = requests.post(
                f"{self._base_api_url}/uploads/logo",
                files=files,
                headers=headers,
                params={"firma_id": self.firm_id},
                timeout=60
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def upload_firma(self, file) -> Dict[str, Any]:
        """Upload attorney signature."""
        try:
            files = {"file": file}
            headers = {"X-Firm-ID": str(self.firm_id)}
            response = requests.post(
                f"{self._base_api_url}/uploads/firma",
                files=files,
                headers=headers,
                params={"firma_id": self.firm_id},
                timeout=60
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # CLIENTS (CLIENTES)
    # =========================================================================

    def listar_clientes(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List all clients for the firm."""
        try:
            response = requests.get(
                f"{self._base_api_url}/clientes/",
                params={"skip": skip, "limit": limit},
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def crear_cliente(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client with all fields."""
        try:
            response = requests.post(
                f"{self._base_api_url}/clientes/",
                json=data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def actualizar_cliente(self, cliente_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a client."""
        try:
            response = requests.put(
                f"{self._base_api_url}/clientes/{cliente_id}",
                json=data,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def bulk_update_clientes(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk update multiple clients."""
        try:
            response = requests.post(
                f"{self._base_api_url}/clientes/bulk-update",
                json={"updates": updates},
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def obtener_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """Get a specific client by ID."""
        try:
            response = requests.get(
                f"{self._base_api_url}/clientes/{cliente_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def eliminar_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """Delete (soft) a client."""
        try:
            response = requests.delete(
                f"{self._base_api_url}/clientes/{cliente_id}",
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # MATTERS (ASUNTOS)
    # =========================================================================

    def listar_asuntos(self, skip: int = 0, limit: int = 100, estado: Optional[str] = None) -> Dict[str, Any]:
        """List all legal matters for the firm."""
        params = {"skip": skip, "limit": limit}
        if estado:
            params["estado"] = estado

        try:
            response = requests.get(
                f"{self._base_api_url}/asuntos/",
                params=params,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    def crear_asunto(
        self,
        cliente_id: int,
        nombre_asunto: str,
        estado: str = "ACTIVO"
    ) -> Dict[str, Any]:
        """Create a new legal matter."""
        payload = {
            "cliente_id": cliente_id,
            "nombre_asunto": nombre_asunto,
            "estado": estado
        }

        try:
            response = requests.post(
                f"{self._base_api_url}/asuntos/",
                json=payload,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)

    # =========================================================================
    # CONFLICT CHECKING
    # =========================================================================

    def verificar_conflicto(
        self,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        segundo_apellido: Optional[str] = None,
        nombre_empresa: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check for conflicts of interest."""
        payload = {}
        if nombre:
            payload["nombre"] = nombre
        if apellido:
            payload["apellido"] = apellido
        if segundo_apellido:
            payload["segundo_apellido"] = segundo_apellido
        if nombre_empresa:
            payload["nombre_empresa"] = nombre_empresa

        try:
            response = requests.post(
                f"{self._base_api_url}/conflictos/verificar",
                json=payload,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return self._handle_error(e)


# Singleton instance
api_client = ProfessionalHubsAPI()

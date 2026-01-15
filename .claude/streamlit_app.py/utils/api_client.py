"""
API Client for Professional Hubs Backend.
Handles all communication with the FastAPI server.
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
            firm_id: Law firm ID for multi-tenant isolation
        """
        self.base_url = base_url or os.getenv(
            "API_BASE_URL", 
            "https://web-professional-hubs.up.railway.app"
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
    # CONFLICT CHECKING
    # =========================================================================
    
    def verificar_conflicto(
        self,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        segundo_apellido: Optional[str] = None,
        nombre_empresa: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for conflicts of interest.
        
        Args:
            nombre: First name
            apellido: First surname
            segundo_apellido: Second surname (PR format)
            nombre_empresa: Company name
        
        Returns:
            Conflict check results
        """
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
        except requests.exceptions.HTTPError as e:
            error_detail = "Error desconocido"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            return {"success": False, "error": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
    
    def get_conflict_service_status(self) -> Dict[str, Any]:
        """Get conflict checking service status."""
        try:
            response = requests.get(
                f"{self._base_api_url}/conflictos/estado",
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
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
            return {"success": False, "error": str(e)}
    
    def crear_cliente(
        self,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        segundo_apellido: Optional[str] = None,
        nombre_empresa: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new client."""
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
                f"{self._base_api_url}/clientes/",
                json=payload,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            error_detail = "Error desconocido"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                pass
            return {"success": False, "error": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
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
            return {"success": False, "error": str(e)}
    
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
            return {"success": False, "error": str(e)}
    
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
            return {"success": False, "error": str(e)}
    
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
        except requests.exceptions.HTTPError as e:
            error_detail = "Error desconocido"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                pass
            return {"success": False, "error": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # RELATED PARTIES (PARTES RELACIONADAS)
    # =========================================================================
    
    def listar_partes_relacionadas(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List all related parties for the firm."""
        try:
            response = requests.get(
                f"{self._base_api_url}/partes-relacionadas/",
                params={"skip": skip, "limit": limit},
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def crear_parte_relacionada(
        self,
        asunto_id: int,
        nombre: str,
        tipo_relacion: str
    ) -> Dict[str, Any]:
        """Create a new related party."""
        payload = {
            "asunto_id": asunto_id,
            "nombre": nombre,
            "tipo_relacion": tipo_relacion
        }
        
        try:
            response = requests.post(
                f"{self._base_api_url}/partes-relacionadas/",
                json=payload,
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            error_detail = "Error desconocido"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                pass
            return {"success": False, "error": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_tipos_relacion(self) -> Dict[str, Any]:
        """Get available relationship types."""
        try:
            response = requests.get(
                f"{self._base_api_url}/partes-relacionadas/tipos/",
                headers=self._headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}


# Singleton instance
api_client = ProfessionalHubsAPI()
"""
Script para poblar la base de datos con datos de ejemplo.
Útil para desarrollo y pruebas.

Ejecutar: python -m scripts.seed_data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Firma, Cliente, Asunto, ParteRelacionada
from app.models.asunto import EstadoAsunto
from app.models.parte_relacionada import TipoRelacion


def crear_datos_ejemplo():
    """Crea datos de ejemplo en la base de datos."""
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Firma).first():
            print("Ya existen datos en la base de datos.")
            print("Para reiniciar, elimine la base de datos y ejecute nuevamente.")
            return
        
        print("Creando datos de ejemplo...")
        
        # ============================================
        # FIRMA 1: Bufete García & Asociados
        # ============================================
        firma1 = Firma(nombre="Bufete García & Asociados")
        db.add(firma1)
        db.flush()
        
        # Clientes de Firma 1
        cliente1 = Cliente(
            firma_id=firma1.id,
            nombre="Juan",
            apellido="García"
        )
        cliente2 = Cliente(
            firma_id=firma1.id,
            nombre="María",
            apellido="Rodríguez"
        )
        cliente3 = Cliente(
            firma_id=firma1.id,
            nombre_empresa="Corporación ABC de Puerto Rico"
        )
        cliente4 = Cliente(
            firma_id=firma1.id,
            nombre="Carlos",
            apellido="Pérez"
        )
        
        db.add_all([cliente1, cliente2, cliente3, cliente4])
        db.flush()
        
        # Asuntos de Firma 1
        asunto1 = Asunto(
            cliente_id=cliente1.id,
            nombre_asunto="García vs. Banco Popular - Ejecución Hipotecaria",
            fecha_apertura=date.today() - timedelta(days=90),
            estado=EstadoAsunto.ACTIVO
        )
        asunto2 = Asunto(
            cliente_id=cliente2.id,
            nombre_asunto="Rodríguez - Divorcio y Custodia",
            fecha_apertura=date.today() - timedelta(days=180),
            estado=EstadoAsunto.CERRADO
        )
        asunto3 = Asunto(
            cliente_id=cliente3.id,
            nombre_asunto="ABC Corp - Disputa Contractual con Proveedor",
            fecha_apertura=date.today() - timedelta(days=30),
            estado=EstadoAsunto.ACTIVO
        )
        asunto4 = Asunto(
            cliente_id=cliente4.id,
            nombre_asunto="Pérez - Accidente de Tránsito",
            fecha_apertura=date.today() - timedelta(days=15),
            estado=EstadoAsunto.PENDIENTE
        )
        
        db.add_all([asunto1, asunto2, asunto3, asunto4])
        db.flush()
        
        # Partes relacionadas de Firma 1
        partes1 = [
            ParteRelacionada(
                asunto_id=asunto1.id,
                nombre="Banco Popular de Puerto Rico",
                tipo_relacion=TipoRelacion.PARTE_CONTRARIA
            ),
            ParteRelacionada(
                asunto_id=asunto2.id,
                nombre="Pedro Rodríguez",
                tipo_relacion=TipoRelacion.DEMANDADO
            ),
            ParteRelacionada(
                asunto_id=asunto2.id,
                nombre="Ana Rodríguez",
                tipo_relacion=TipoRelacion.CONYUGE
            ),
            ParteRelacionada(
                asunto_id=asunto3.id,
                nombre="Distribuidora XYZ",
                tipo_relacion=TipoRelacion.DEMANDADO
            ),
            ParteRelacionada(
                asunto_id=asunto3.id,
                nombre="XYZ Holdings Inc.",
                tipo_relacion=TipoRelacion.EMPRESA_MATRIZ
            ),
            ParteRelacionada(
                asunto_id=asunto4.id,
                nombre="José Martínez",
                tipo_relacion=TipoRelacion.DEMANDADO
            ),
            ParteRelacionada(
                asunto_id=asunto4.id,
                nombre="Seguros Universal",
                tipo_relacion=TipoRelacion.PARTE_CONTRARIA
            ),
        ]
        db.add_all(partes1)
        
        # ============================================
        # FIRMA 2: Hernández Law Office
        # ============================================
        firma2 = Firma(nombre="Hernández Law Office")
        db.add(firma2)
        db.flush()
        
        # Clientes de Firma 2
        cliente5 = Cliente(
            firma_id=firma2.id,
            nombre="Luis",
            apellido="Hernández"
        )
        cliente6 = Cliente(
            firma_id=firma2.id,
            nombre_empresa="Tech Solutions PR LLC"
        )
        
        db.add_all([cliente5, cliente6])
        db.flush()
        
        # Asuntos de Firma 2
        asunto5 = Asunto(
            cliente_id=cliente5.id,
            nombre_asunto="Hernández - Planificación Sucesoral",
            fecha_apertura=date.today() - timedelta(days=60),
            estado=EstadoAsunto.ACTIVO
        )
        asunto6 = Asunto(
            cliente_id=cliente6.id,
            nombre_asunto="Tech Solutions - Registro de Marca",
            fecha_apertura=date.today() - timedelta(days=45),
            estado=EstadoAsunto.ARCHIVADO
        )
        
        db.add_all([asunto5, asunto6])
        db.flush()
        
        # Partes relacionadas de Firma 2
        partes2 = [
            ParteRelacionada(
                asunto_id=asunto5.id,
                nombre="Rosa Hernández",
                tipo_relacion=TipoRelacion.CONYUGE
            ),
            ParteRelacionada(
                asunto_id=asunto6.id,
                nombre="Tech Solutions USA Inc.",
                tipo_relacion=TipoRelacion.EMPRESA_MATRIZ
            ),
        ]
        db.add_all(partes2)
        
        # Commit todo
        db.commit()
        
        print("=" * 50)
        print("DATOS DE EJEMPLO CREADOS EXITOSAMENTE")
        print("=" * 50)
        print(f"\nFirma 1: {firma1.nombre} (ID: {firma1.id})")
        print(f"  - 4 clientes")
        print(f"  - 4 asuntos")
        print(f"  - 7 partes relacionadas")
        print(f"\nFirma 2: {firma2.nombre} (ID: {firma2.id})")
        print(f"  - 2 clientes")
        print(f"  - 2 asuntos")
        print(f"  - 2 partes relacionadas")
        print("\n" + "=" * 50)
        print("PARA PROBAR LA API:")
        print("=" * 50)
        print(f"\n1. Iniciar servidor:")
        print(f"   uvicorn app.main:app --reload")
        print(f"\n2. Probar verificación de conflictos:")
        print(f'   curl -X POST "http://localhost:8000/api/v1/conflictos/verificar" \\')
        print(f'     -H "X-Firm-ID: {firma1.id}" \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -d \'{{"nombre": "Juan", "apellido": "García"}}\'')
        print(f"\n3. Documentación interactiva:")
        print(f"   http://localhost:8000/docs")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    crear_datos_ejemplo()
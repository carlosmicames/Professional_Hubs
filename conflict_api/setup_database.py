"""
Simple script to create all database tables.
Run this once to set up the database.
"""

from app.database import engine, Base
from app.models import Firma, Cliente, Asunto, ParteRelacionada

# Import models to register them
print("Creating all database tables...")

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All tables created successfully!")
print("\nTables created:")
print("- firmas")
print("- clientes") 
print("- asuntos")
print("- partes_relacionadas")
print("- invoices")
print("- billing_communication_logs")
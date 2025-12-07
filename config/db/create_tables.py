"""
Skrypt do utworzenia tabel w bazie danych
Uruchom ten skrypt, aby utworzyć wszystkie tabele zdefiniowane w modelach
"""
import os
import sys
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Upewnij się, że katalog główny projektu jest w sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Importy
try:
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # Importuj Base z config.db.connection
    from config.db.connection import Base

    # Importuj wszystkie modele, aby były zarejestrowane z Base
    from models.menu import MenuItem, MenuCategory
    from models.orders import RestaurantOrder, OrderStatus, OrderType
    from models.reservations import Reservation, ReservationStatus
    from models.tasks import Task, StaffType, TaskStatus, TaskPriority

    # Konfiguracja bazy danych
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/api")
    engine = create_engine(DATABASE_URL)

    logger.info(f"Połączenie z bazą danych: {DATABASE_URL}")

    # Sprawdź połączenie z bazą danych
    try:
        connection = engine.connect()
        logger.info("Połączenie z bazą danych powiodło się!")
        connection.close()
    except Exception as e:
        logger.error(f"Nie można połączyć się z bazą danych: {e}")
        sys.exit(1)

    # Sprawdź istniejące tabele
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    logger.info(f"Istniejące tabele przed utworzeniem: {existing_tables}")

    # Utwórz tabele
    logger.info("Tworzenie tabel...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabele zostały utworzone!")

    # Sprawdź tabele po utworzeniu
    inspector = inspect(engine)
    tables_after = inspector.get_table_names()
    logger.info(f"Tabele po utworzeniu: {tables_after}")

    # Pokaż nowe tabele
    new_tables = set(tables_after) - set(existing_tables)
    if new_tables:
        logger.info(f"Nowo utworzone tabele: {new_tables}")
    else:
        logger.info("Nie utworzono nowych tabel. Wszystkie tabele już istnieją.")

except ImportError as e:
    logger.error(f"Błąd importu: {e}")
    logger.error("Upewnij się, że struktura projektu jest poprawna i wszystkie moduły są dostępne.")
    sys.exit(1)
except Exception as e:
    logger.error(f"Wystąpił nieoczekiwany błąd: {e}")
    sys.exit(1)
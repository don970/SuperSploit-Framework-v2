import sqlite3
import os
from .database import DatabaseManagment

class ServiceDBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            install = DatabaseManagment.getInstall()
            self.db_path = os.path.join(install, ".data", ".config", "signatures.db")
        else:
            self.db_path = db_path

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found. Please run 'up-service-db'.")

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def get_all_matches(self):
        """Retrieves all service matches from the DB for memory caching."""
        conn = self.get_conn()
        curr = conn.cursor()
        # We only grab match data for now to populate the regex engine
        query = '''
            SELECT service, pattern 
            FROM service_matches
        '''
        curr.execute(query)
        results = curr.fetchall()
        conn.close()
        return results

    # Probes logic can be expanded here for active multi-stage probing
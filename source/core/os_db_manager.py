import sqlite3
import os
from .database import DatabaseManagment

class OSDBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            install = DatabaseManagment.getInstall()
            self.db_path = os.path.join(install, ".data", ".config", "signatures.db")
        else:
            self.db_path = db_path

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}. Please run migrator.")

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def find_candidates_by_test(self, test_name, result_string):
        """
        Quickly finds fingerprints that match a specific test result.
        Example: test_name='T1', result_string='R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R'
        """
        conn = self.get_conn()
        curr = conn.cursor()
        
        # Using simple string matching for the demo, but logic can be expanded 
        # to handle Nmap's range and 'OR' syntax.
        query = '''
            SELECT f.name, c.vendor, c.os_family 
            FROM fingerprints f
            JOIN fingerprint_tests t ON f.id = t.fp_id
            JOIN fingerprint_classes c ON f.id = c.fp_id
            WHERE t.test_name = ? AND t.test_values = ?
        '''
        curr.execute(query, (test_name, result_string))
        results = curr.fetchall()
        conn.close()
        return results

    def get_fingerprint_details(self, fp_name):
        """Returns all test data for a specific fingerprint."""
        conn = self.get_conn()
        curr = conn.cursor()
        curr.execute("SELECT test_name, test_values FROM fingerprint_tests JOIN fingerprints ON fingerprints.id = fingerprint_tests.fp_id WHERE fingerprints.name = ?", (fp_name,))
        data = curr.fetchall()
        conn.close()
        return {row[0]: row[1] for row in data}
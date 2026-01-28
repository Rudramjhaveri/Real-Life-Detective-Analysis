import sqlite3
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class SQLEngine:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def execute_query(self, query):
        """
        Loads CSV into in-memory SQLite and runs the query.
        Returns:
            - success (bool)
            - data (list of dicts or None)
            - columns (list or None)
            - error (str or None)
        """
        conn = None
        try:
            # 1. Create In-Memory DB
            conn = sqlite3.connect(':memory:')
            
            # 2. Load CSV
            # Optimization: In production, we might want to cache this DB or use a real DB
            df = pd.read_csv(self.dataset_path)
            
            # Sanitize column names if needed (simple approach for now)
            # df.columns = [c.replace(' ', '_') for c in df.columns] 
            
            df.to_sql('dataset', conn, index=False, if_exists='replace')

            # 3. Execute Query
            # Using pandas read_sql to easily get result as DataFrame
            result_df = pd.read_sql_query(query, conn)
            
            # 4. Format Output
            columns = result_df.columns.tolist()
            # Convert to list of lists for lighter transport, or dict records
            data = result_df.head(50).values.tolist() # Limit to 50 rows for preview
            
            return {
                'success': True,
                'columns': columns,
                'rows': data,
                'row_count': len(result_df),
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'columns': [],
                'rows': [],
                'error': str(e)
            }
        finally:
            if conn:
                conn.close()

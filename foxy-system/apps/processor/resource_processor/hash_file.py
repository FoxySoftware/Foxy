import hashlib

import sqlite3
import hashlib

def hash_table_data(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Hash object
    hash_obj = hashlib.sha256()
    
    for row in rows:
        # Convert each row into a sorted tuple and update hash
        hash_obj.update(str(tuple(sorted(str(row)))).encode('utf-8'))
    
    return hash_obj.hexdigest()

def hash_database(database_path):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        db_hash_obj = hashlib.sha256()
        
        for table in sorted(tables):
            table_hash = hash_table_data(cursor, table)
            db_hash_obj.update(table_hash.encode('utf-8'))
        
        return db_hash_obj.hexdigest()


def hash_file(file_path, algorithm='md5'):
    hash_algo = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_algo.update(chunk)
    
    return hash_algo.hexdigest()

if __name__ == "__main__":
    #file_path = 'test_table_db.db'
    #file_hash = hash_file(file_path, 'sha256')
    #print(f'Hash : {file_hash}')
    
    db_hash = hash_database('test_table_db.db')


    print(f"Database hash: {db_hash}")




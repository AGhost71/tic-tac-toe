import sqlite3
class database():
    def __init__(self):
        self.conn = sqlite3.connect('tic.db')

        # Create a cursor object
        self.cursor = self.conn.cursor()

        # SQL command to create the 'records' table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            total INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            UNIQUE(telegram_id, chat_id)
        );
        '''

        # Execute the SQL command
        self.cursor.execute(create_table_query)

        # Commit the changes
        self.conn.commit()

    def add_user(self,telegram_id,chat_id):
        insert_query = '''
        INSERT OR IGNORE INTO records (telegram_id, chat_id)
        VALUES (?, ?);
        '''

        # Execute the SQL command
        self.cursor.execute(insert_query, (telegram_id, chat_id,))

        # Commit the changes
        self.conn.commit()
    def update_record(self,telegram_id,chat_id,win):
        if win:
            update_query = '''
            UPDATE records
            SET total = total + 1, wins = wins + 1
            WHERE telegram_id = ? AND chat_id = ?;
            '''
        else:
            update_query = '''
                UPDATE records
                SET total = total + 1
                WHERE telegram_id = ? AND chat_id = ?;
                '''

        # Execute the SQL command
        self.cursor.execute(update_query, (telegram_id, chat_id))
        self.conn.commit()
    def chat_record(self,chat_id):
        # SQL command to select all records
        select_query = '''SELECT * FROM records WHERE chat_id = ?;'''

        # Execute the SQL command
        self.cursor.execute(select_query,(int(chat_id),))

        # Fetch all records from the executed query
        records = self.cursor.fetchall()
        return records
    def close(self):
        self.conn.close()

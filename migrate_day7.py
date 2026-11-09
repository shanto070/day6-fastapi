
import sqlite3

DATABASE = "users.db"

connection = sqlite3.connect(DATABASE)

try:
    connection.execute("BEGIN")

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    }

    if "password_hash" not in columns:
        connection.execute(
            "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"
        )
        print("Added password_hash column")

    if "role" not in columns:
        connection.execute(
            """
            ALTER TABLE users
            ADD COLUMN role VARCHAR(20)
            NOT NULL DEFAULT 'user'
            """
        )
        print("Added role column")

    connection.commit()
    print("Database migration completed successfully!")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()

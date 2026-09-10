from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine


def main():
    safe_url = settings.database_url.replace("export_dev_password", "***")
    print(f"Connecting with: {safe_url}")

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT current_user, current_database(), "
                "inet_server_addr()::text, inet_server_port()"
            )
        ).one()

    print("Database connection: OK")
    print(f"User: {row[0]}")
    print(f"Database: {row[1]}")
    print(f"Server address: {row[2]}")
    print(f"Server port inside container: {row[3]}")


if __name__ == "__main__":
    main()

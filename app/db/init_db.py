from repository import Repository


def init_db():
    """Create all database tables."""
    repository = Repository()
    repository.create_tables()
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()

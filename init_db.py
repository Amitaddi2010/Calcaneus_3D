from database import Base, database_url
from sqlalchemy import create_engine

def init_database():
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database() 
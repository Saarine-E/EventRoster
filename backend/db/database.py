from sqlmodel import SQLModel, Session, create_engine

db_filename = "eventroster.db"
connect_args = {"check_same_thread":False}
engine = create_engine(f"sqlite:///db/{db_filename}", echo=True,connect_args=connect_args)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
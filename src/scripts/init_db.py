import src.db  # This declares all database tables


src.db.Base.metadata.create_all(src.db.Engine)

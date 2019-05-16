import sqlalchemy

from fx_service.config import DATABASE_URL

metadata = sqlalchemy.MetaData()

rm_fx_quote = sqlalchemy.Table(
    "rm_fx_quote",
    metadata,
    sqlalchemy.Column("symbol", sqlalchemy.String(length=6)),
    sqlalchemy.Column("bid", sqlalchemy.Float),
    sqlalchemy.Column("ask", sqlalchemy.Float),
    sqlalchemy.Column("price", sqlalchemy.Float),
    sqlalchemy.Column("timestamp", sqlalchemy.TIMESTAMP(timezone=True)),
)


def insert_fx_quotes(values):
    engine = sqlalchemy.create_engine(DATABASE_URL)
    query = rm_fx_quote.insert()
    with engine.connect() as conn:
        conn.execute(query, values)

import sqlalchemy

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

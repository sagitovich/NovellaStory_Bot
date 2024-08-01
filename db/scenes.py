from db.db_gino import BaseModel
from sqlalchemy import Column, BigInteger, ARRAY, VARCHAR, sql


class Scenes(BaseModel):
    __tablename__ = 'scenes'
    user_id = Column(BigInteger, primary_key=True)
    scenes = Column(ARRAY(BigInteger))
    media = Column(ARRAY(VARCHAR))

    query: sql.select

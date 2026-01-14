from sqlalchemy import Column, String, Date
from db.base import Base

class Policy(Base):
    __tablename__ = "policy"

    aadhaar_no = Column(String, primary_key=True, index=True)
    policy_name = Column(String, nullable=False)
    policy_expiry = Column(Date, nullable=False)

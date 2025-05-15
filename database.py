import os
import datetime
import json
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create SQLAlchemy Base
Base = declarative_base()

# Get database URL from environment variable
database_url = os.environ.get('DATABASE_URL')

# Patient model
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_id={self.patient_id})>"

# Analysis model
class Analysis(Base):
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    foot_side = Column(String(20), nullable=False)
    analysis_date = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="analyses")
    screws = relationship("Screw", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, foot_side={self.foot_side})>"

# Screw model
class Screw(Base):
    __tablename__ = 'screws'
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analyses.id'))
    screw_number = Column(Integer, nullable=False)
    medial_shortest_positive = Column(Float, nullable=True)
    medial_longest_negative = Column(Float, nullable=True)
    lateral_shortest_positive = Column(Float, nullable=True)
    lateral_longest_negative = Column(Float, nullable=True)
    has_medial_breach = Column(Boolean, default=False)
    has_lateral_breach = Column(Boolean, default=False)
    
    # Store visualization data as JSON
    axis_points = Column(Text, nullable=True)  # JSON string
    signed_medial = Column(Text, nullable=True)  # JSON string
    signed_lateral = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    analysis = relationship("Analysis", back_populates="screws")
    
    def __repr__(self):
        return f"<Screw(id={self.id}, screw_number={self.screw_number})>"
    
    @classmethod
    def from_result_dict(cls, result_dict: Dict[str, Any], screw_number: int, analysis_id: int) -> 'Screw':
        """
        Create a Screw instance from a result dictionary
        """
        # Convert numpy arrays to JSON-serializable lists
        axis_points = json.dumps(result_dict['axis_points'].tolist()) if 'axis_points' in result_dict else None
        signed_medial = json.dumps(result_dict['signed_medial'].tolist()) if 'signed_medial' in result_dict else None
        signed_lateral = json.dumps(result_dict['signed_lateral'].tolist()) if 'signed_lateral' in result_dict else None
        
        medial_breach = not np.isnan(result_dict['medial_longest_negative']) if 'medial_longest_negative' in result_dict else False
        lateral_breach = not np.isnan(result_dict['lateral_longest_negative']) if 'lateral_longest_negative' in result_dict else False
        
        return cls(
            analysis_id=analysis_id,
            screw_number=screw_number,
            medial_shortest_positive=float(result_dict.get('medial_shortest_positive', 0)),
            medial_longest_negative=float(result_dict.get('medial_longest_negative', 0)) if medial_breach else None,
            lateral_shortest_positive=float(result_dict.get('lateral_shortest_positive', 0)),
            lateral_longest_negative=float(result_dict.get('lateral_longest_negative', 0)) if lateral_breach else None,
            has_medial_breach=medial_breach,
            has_lateral_breach=lateral_breach,
            axis_points=axis_points,
            signed_medial=signed_medial,
            signed_lateral=signed_lateral
        )

# Database connection and session
class Database:
    def __init__(self):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)
        
    def get_session(self):
        """Get a new session"""
        return self.Session()
    
    def add_patient(self, patient_id: str, name: Optional[str] = None, 
                   age: Optional[int] = None, gender: Optional[str] = None) -> Patient:
        """Add a new patient to the database"""
        session = self.get_session()
        try:
            patient = Patient(patient_id=patient_id, name=name, age=age, gender=gender)
            session.add(patient)
            session.commit()
            return patient
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get a patient by their ID"""
        session = self.get_session()
        try:
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            return patient
        finally:
            session.close()
    
    def get_all_patients(self) -> List[Patient]:
        """Get all patients"""
        session = self.get_session()
        try:
            patients = session.query(Patient).all()
            return patients
        finally:
            session.close()
    
    def add_analysis(self, patient_id: str, foot_side: str, results: List[Dict[str, Any]], 
                     notes: Optional[str] = None) -> Analysis:
        """Add a new analysis with screws to the database"""
        session = self.get_session()
        try:
            # Get or create patient
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                patient = Patient(patient_id=patient_id)
                session.add(patient)
                session.flush()
            
            # Create analysis
            analysis = Analysis(patient_id=patient.id, foot_side=foot_side, notes=notes)
            session.add(analysis)
            session.flush()
            
            # Add screws
            for i, result in enumerate(results):
                screw = Screw.from_result_dict(result, i + 1, analysis.id)
                session.add(screw)
            
            session.commit()
            return analysis
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_analyses_for_patient(self, patient_id: str) -> List[Analysis]:
        """Get all analyses for a patient"""
        session = self.get_session()
        try:
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                return []
            
            analyses = session.query(Analysis).filter(Analysis.patient_id == patient.id).all()
            return analyses
        finally:
            session.close()
    
    def get_screws_for_analysis(self, analysis_id: int) -> List[Screw]:
        """Get all screws for an analysis"""
        session = self.get_session()
        try:
            screws = session.query(Screw).filter(Screw.analysis_id == analysis_id).all()
            return screws
        finally:
            session.close()

# Initialize database
db = Database()

def init_db():
    """Initialize the database by creating all tables"""
    db.create_tables()
    print("Database tables created.")

if __name__ == "__main__":
    init_db()
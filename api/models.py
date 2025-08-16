"""Database models for FLL-Sim API"""

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_student = Column(Boolean, default=True)
    is_instructor = Column(Boolean, default=False)
    grade_level = Column(String(20))
    class_section = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    simulation_results = relationship("SimulationResult", back_populates="user")
    progress_records = relationship("ProgressRecord", back_populates="user")


class Mission(Base):
    """Mission model"""
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty_level = Column(Integer, default=1)
    season = Column(String(50))
    objectives = Column(Text)  # JSON string
    scoring_criteria = Column(Text)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    simulation_results = relationship("SimulationResult", back_populates="mission")


class SimulationResult(Base):
    """Simulation result model"""
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    score = Column(Integer, default=0)
    completion_time = Column(Integer)  # seconds
    success = Column(Boolean, default=False)
    program_code = Column(Text)
    error_log = Column(Text)
    robot_path = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="simulation_results")
    mission = relationship("Mission", back_populates="simulation_results")


class ProgressRecord(Base):
    """Student progress tracking"""
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50))  # tutorial, mission, visual_programming
    activity_id = Column(String(100))
    status = Column(String(20))  # started, completed, failed
    progress_data = Column(Text)  # JSON string
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress_records")
    user = relationship("User", back_populates="progress_records")

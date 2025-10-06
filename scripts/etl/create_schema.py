#!/usr/bin/env python3
"""
Create database schema for StreamWatch data
"""

import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database_schema():
    """Create the database schema for StreamWatch data"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Creating StreamWatch database schema...")
        
        with engine.connect() as conn:
            # Create sites table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sites (
                    site_code VARCHAR(20) PRIMARY KEY,
                    is_active BOOLEAN,
                    groundtruthing_priority VARCHAR(50),
                    groundtruthing_status VARCHAR(50),
                    waterbody VARCHAR(100),
                    subwatershed VARCHAR(100),
                    description TEXT,
                    property_type VARCHAR(50),
                    permission VARCHAR(50),
                    walk_time VARCHAR(50),
                    walk_distance VARCHAR(50),
                    walk_gradient VARCHAR(50),
                    water_access VARCHAR(50),
                    additional_comments TEXT,
                    environmental_hazards TEXT,
                    parking_details TEXT,
                    walking_directions TEXT,
                    habitat_type VARCHAR(50),
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    site_type VARCHAR(50),
                    cat_priority VARCHAR(50),
                    cat_status VARCHAR(50),
                    last_cat_sample_date DATE,
                    bat_priority VARCHAR(50),
                    bat_status VARCHAR(50),
                    last_bat_sample_date DATE,
                    bact_priority VARCHAR(50),
                    bact_status VARCHAR(50),
                    drainage_area DECIMAL(10, 2)
                )
            """))
            
            # Create samples table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS samples (
                    sample_id VARCHAR(50) PRIMARY KEY,
                    site_code VARCHAR(20),
                    sample_date DATE,
                    sample_time TIME,
                    water_temperature DECIMAL(5, 2),
                    ph DECIMAL(4, 2),
                    do_ppm DECIMAL(6, 2),
                    do_percent DECIMAL(5, 2),
                    nitrate DECIMAL(8, 3),
                    phosphates DECIMAL(8, 3),
                    turbidity DECIMAL(8, 2),
                    conductivity DECIMAL(8, 2),
                    total_solids DECIMAL(8, 2),
                    total_suspended_solids DECIMAL(8, 2),
                    total_dissolved_solids DECIMAL(8, 2),
                    alkalinity DECIMAL(8, 2),
                    hardness DECIMAL(8, 2),
                    chloride DECIMAL(8, 2),
                    sulfate DECIMAL(8, 2),
                    calcium DECIMAL(8, 2),
                    magnesium DECIMAL(8, 2),
                    sodium DECIMAL(8, 2),
                    potassium DECIMAL(8, 2),
                    iron DECIMAL(8, 2),
                    manganese DECIMAL(8, 2),
                    copper DECIMAL(8, 2),
                    zinc DECIMAL(8, 2),
                    lead DECIMAL(8, 2),
                    cadmium DECIMAL(8, 2),
                    chromium DECIMAL(8, 2),
                    nickel DECIMAL(8, 2),
                    mercury DECIMAL(8, 2),
                    arsenic DECIMAL(8, 2),
                    selenium DECIMAL(8, 2),
                    aluminum DECIMAL(8, 2),
                    boron DECIMAL(8, 2),
                    fluoride DECIMAL(8, 2),
                    silica DECIMAL(8, 2),
                    total_nitrogen DECIMAL(8, 2),
                    total_phosphorus DECIMAL(8, 2),
                    ammonia DECIMAL(8, 2),
                    nitrite DECIMAL(8, 2),
                    organic_nitrogen DECIMAL(8, 2),
                    organic_phosphorus DECIMAL(8, 2),
                    inorganic_phosphorus DECIMAL(8, 2),
                    total_carbon DECIMAL(8, 2),
                    organic_carbon DECIMAL(8, 2),
                    inorganic_carbon DECIMAL(8, 2),
                    total_organic_carbon DECIMAL(8, 2),
                    dissolved_organic_carbon DECIMAL(8, 2),
                    particulate_organic_carbon DECIMAL(8, 2),
                    biochemical_oxygen_demand DECIMAL(8, 2),
                    chemical_oxygen_demand DECIMAL(8, 2),
                    total_coliforms DECIMAL(10, 0),
                    fecal_coliforms DECIMAL(10, 0),
                    e_coli DECIMAL(10, 0),
                    enterococci DECIMAL(10, 0),
                    heterotrophic_plate_count DECIMAL(10, 0),
                    total_heterotrophic_bacteria DECIMAL(10, 0),
                    total_plate_count DECIMAL(10, 0),
                    total_bacteria DECIMAL(10, 0),
                    FOREIGN KEY (site_code) REFERENCES sites(site_code)
                )
            """))
            
            # Create bugs table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bugs (
                    bug_record_id VARCHAR(100) PRIMARY KEY,
                    sample_code VARCHAR(50),
                    order_name VARCHAR(50),
                    family VARCHAR(100),
                    count INTEGER,
                    percentage DECIMAL(5, 2),
                    tolerance DECIMAL(3, 1),
                    ept BOOLEAN,
                    insect BOOLEAN,
                    sensitive BOOLEAN,
                    scraper BOOLEAN,
                    clinger BOOLEAN,
                    product_ftv DECIMAL(8, 2),
                    product_tolerance DECIMAL(8, 2),
                    talu_attribute VARCHAR(10),
                    ftv DECIMAL(3, 1)
                )
            """))
            
            # Create bacteria table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bacteria (
                    bacteria_record_id VARCHAR(100) PRIMARY KEY,
                    sample_code VARCHAR(50),
                    site_code VARCHAR(20),
                    collection_date DATE,
                    collection_time TIME,
                    measurement_value VARCHAR(50),
                    water_temperature DECIMAL(5, 2),
                    turbidity DECIMAL(8, 2),
                    ph DECIMAL(4, 2),
                    do_ppm DECIMAL(6, 2),
                    conductivity DECIMAL(8, 2),
                    total_coliforms DECIMAL(10, 0),
                    fecal_coliforms DECIMAL(10, 0),
                    e_coli DECIMAL(10, 0),
                    enterococci DECIMAL(10, 0),
                    FOREIGN KEY (site_code) REFERENCES sites(site_code)
                )
            """))
            
            # Create volunteers table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS volunteers (
                    volunteer_id VARCHAR(20) PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    full_name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT,
                    city VARCHAR(50),
                    state VARCHAR(2),
                    zip_code VARCHAR(10),
                    start_date DATE,
                    active_cat BOOLEAN,
                    active_bat BOOLEAN,
                    active_bact BOOLEAN,
                    training_status VARCHAR(50),
                    notes TEXT
                )
            """))
            
            # Create taxonomy table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS taxonomy (
                    bug_id VARCHAR(20) PRIMARY KEY,
                    family VARCHAR(100),
                    genus_species VARCHAR(100),
                    tolerance_value DECIMAL(3, 1),
                    ept BOOLEAN,
                    insect BOOLEAN,
                    functional_group VARCHAR(50),
                    habitat_preference VARCHAR(50),
                    pollution_tolerance VARCHAR(50),
                    notes TEXT
                )
            """))
            
            # Create indices for better performance
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_samples_site_code ON samples(site_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_samples_date ON samples(sample_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bugs_sample_code ON bugs(sample_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bacteria_site_code ON bacteria(site_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bacteria_date ON bacteria(collection_date)"))
            
            conn.commit()
            
        logger.info("Database schema created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        return False

if __name__ == "__main__":
    create_database_schema()

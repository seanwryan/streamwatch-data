#!/usr/bin/env python3
"""
Create additional database tables for StreamWatch data
This script adds the remaining 8 tables to complete the 14-table schema
"""

import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_additional_tables():
    """Create the additional 8 tables for StreamWatch data"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Creating additional StreamWatch database tables...")
        
        with engine.connect() as conn:
            # Create sample_dates table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sample_dates (
                    sample_id INTEGER PRIMARY KEY,
                    station VARCHAR(20),
                    sample_date DATE,
                    sample_code VARCHAR(50)
                )
            """))
            
            # Create bug_results table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bug_results (
                    bug_result_id SERIAL PRIMARY KEY,
                    sample_id INTEGER,
                    sample_code VARCHAR(50),
                    bug_id INTEGER,
                    family VARCHAR(100),
                    genus_species VARCHAR(100),
                    exclude BOOLEAN,
                    amount INTEGER
                )
            """))
            
            # Create rbp100_bugs table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS rbp100_bugs (
                    rbp_id INTEGER PRIMARY KEY,
                    sample_id INTEGER,
                    sample_code VARCHAR(50),
                    bug_id INTEGER,
                    family VARCHAR(100),
                    genus_species VARCHAR(100),
                    amount INTEGER
                )
            """))
            
            # Create bug_list table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bug_list (
                    bug_id INTEGER PRIMARY KEY,
                    order_class VARCHAR(50),
                    family VARCHAR(100),
                    genus_species VARCHAR(100),
                    genus VARCHAR(100),
                    genus_id INTEGER,
                    adult BOOLEAN,
                    ept BOOLEAN,
                    tanytarsini BOOLEAN,
                    orthocladiinae BOOLEAN,
                    tanypodinae BOOLEAN,
                    insect BOOLEAN,
                    exclude BOOLEAN,
                    ftv DECIMAL(3, 1),
                    ftv_ref VARCHAR(100),
                    ffg VARCHAR(50),
                    ffg_ref VARCHAR(100),
                    tol_val DECIMAL(3, 1),
                    tol_val_ref VARCHAR(100),
                    ny_tol_val DECIMAL(3, 1),
                    synonyms TEXT,
                    habit VARCHAR(100),
                    talu_attribute VARCHAR(50),
                    common_name VARCHAR(100),
                    tsn VARCHAR(50),
                    hide BOOLEAN,
                    amount INTEGER,
                    bug_updated DATE
                )
            """))
            
            # Create cat_meters table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cat_meters (
                    meter_id VARCHAR(20) PRIMARY KEY,
                    volunteer VARCHAR(200),
                    serial_number VARCHAR(50),
                    probe_id VARCHAR(50),
                    meter_type VARCHAR(50),
                    status VARCHAR(50),
                    last_calibration_date DATE,
                    notes TEXT
                )
            """))
            
            # Create cat_assignments table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cat_assignments (
                    assignment_id SERIAL PRIMARY KEY,
                    meter_id VARCHAR(20),
                    volunteer VARCHAR(200),
                    site1 VARCHAR(20),
                    site2 VARCHAR(20),
                    site3 VARCHAR(20),
                    assignment_date DATE,
                    status VARCHAR(50),
                    notes TEXT,
                    FOREIGN KEY (meter_id) REFERENCES cat_meters(meter_id)
                )
            """))
            
            # Create wqx_sites table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS wqx_sites (
                    monitoring_location_id VARCHAR(50) PRIMARY KEY,
                    monitoring_location_name VARCHAR(200),
                    monitoring_location_type_name VARCHAR(100),
                    tribal_land_indicator BOOLEAN,
                    tribal_land_name VARCHAR(200),
                    latitude_measure DECIMAL(10, 8),
                    longitude_measure DECIMAL(11, 8),
                    source_map_scale_numeric INTEGER,
                    horizontal_collection_method_name VARCHAR(100),
                    horizontal_coordinate_reference_system_datum_name VARCHAR(100),
                    state_code VARCHAR(2),
                    county_name VARCHAR(100),
                    auto_generated_county_code VARCHAR(10),
                    huc_eight_digit_code VARCHAR(8),
                    huc_twelve_digit_code VARCHAR(12)
                )
            """))
            
            # Create wqx_biohabphys table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS wqx_biohabphys (
                    wqx_record_id SERIAL PRIMARY KEY,
                    project_id VARCHAR(100),
                    monitoring_location_id VARCHAR(50),
                    activity_id_child VARCHAR(100),
                    activity_id_user_supplied VARCHAR(100),
                    activity_type VARCHAR(100),
                    activity_media_name VARCHAR(100),
                    activity_start_date DATE,
                    activity_start_time TIME,
                    activity_start_time_zone VARCHAR(10),
                    activity_depth_height_measure DECIMAL(8, 2),
                    activity_depth_height_unit VARCHAR(20),
                    assemblage_sampled_name VARCHAR(100),
                    habitat_selection_method VARCHAR(100),
                    collection_area_measure DECIMAL(8, 2),
                    collection_area_unit VARCHAR(20),
                    collection_duration_measure DECIMAL(8, 2),
                    collection_duration_unit VARCHAR(20),
                    gear_procedure_unit_measure DECIMAL(8, 2),
                    gear_procedure_unit_code VARCHAR(20),
                    sampling_component_name VARCHAR(100),
                    result_sampling_point_place_in_series INTEGER,
                    reach_length_measure DECIMAL(8, 2),
                    reach_length_unit VARCHAR(20),
                    reach_width_measure DECIMAL(8, 2),
                    reach_width_unit VARCHAR(20),
                    sample_collection_method_id VARCHAR(100),
                    sample_collection_method_context VARCHAR(100),
                    sample_collection_equipment_name VARCHAR(100),
                    sample_collection_equipment_comment TEXT,
                    net_mesh_size_measure DECIMAL(8, 2),
                    net_mesh_size_unit VARCHAR(20),
                    net_type VARCHAR(100),
                    net_surface_area_measure DECIMAL(8, 2),
                    net_surface_area_unit VARCHAR(20),
                    boat_speed_measure DECIMAL(8, 2),
                    boat_speed_unit VARCHAR(20),
                    characteristic_name VARCHAR(100),
                    characteristic_name_user_supplied VARCHAR(100),
                    method_speciation VARCHAR(100),
                    result_detection_condition VARCHAR(100),
                    result_value VARCHAR(100),
                    result_unit VARCHAR(20),
                    result_sample_fraction VARCHAR(100),
                    result_status_id VARCHAR(50),
                    statistical_base_code VARCHAR(50),
                    result_value_type VARCHAR(50),
                    result_weight_basis VARCHAR(50),
                    result_sampling_point_name VARCHAR(100),
                    result_sampling_point_type VARCHAR(100),
                    biological_intent VARCHAR(100),
                    biological_individual_id VARCHAR(100),
                    subject_taxonomic_name VARCHAR(200),
                    subject_taxonomic_name_user_supplied VARCHAR(200),
                    subject_taxonomic_name_user_supplied_reference_text TEXT,
                    unidentified_species_id VARCHAR(100),
                    sample_tissue_anatomy VARCHAR(100),
                    group_summary_weight_value DECIMAL(10, 3),
                    group_summary_weight_unit VARCHAR(20),
                    group_summary_count INTEGER,
                    proportion_sample_processed_numeric DECIMAL(5, 3),
                    target_count INTEGER,
                    frequency_class_descriptor VARCHAR(100),
                    frequency_class_descriptor_unit VARCHAR(20),
                    lower_class_bound DECIMAL(8, 2),
                    upper_class_bound DECIMAL(8, 2),
                    taxon_cell_form VARCHAR(100),
                    taxon_cell_shape VARCHAR(100),
                    taxon_habit VARCHAR(100),
                    taxon_voltinism VARCHAR(100),
                    taxon_pollution_tolerance VARCHAR(100),
                    taxon_pollution_tolerance_scale VARCHAR(100),
                    taxon_trophic_level VARCHAR(100),
                    taxon_functional_feeding_group VARCHAR(100),
                    result_analytical_method_id VARCHAR(100),
                    result_analytical_method_context VARCHAR(100),
                    analysis_start_date DATE,
                    result_detection_quantitation_limit_type VARCHAR(100),
                    result_detection_quantitation_limit_measure DECIMAL(10, 3),
                    result_detection_quantitation_limit_unit VARCHAR(20),
                    laboratory_name VARCHAR(200),
                    taxon_citation_id VARCHAR(100),
                    result_comment TEXT,
                    activity_group_id VARCHAR(100),
                    activity_group_type VARCHAR(100),
                    activity_group_name VARCHAR(100),
                    result_sampling_point_comment_text TEXT,
                    result_depth_altitude_reference_point VARCHAR(100),
                    result_depth_height_measure DECIMAL(8, 2),
                    result_depth_height_unit VARCHAR(20)
                )
            """))
            
            # Create indices for better performance
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sample_dates_station ON sample_dates(station)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sample_dates_date ON sample_dates(sample_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bug_results_sample_id ON bug_results(sample_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_bug_results_bug_id ON bug_results(bug_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rbp100_bugs_sample_id ON rbp100_bugs(sample_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_cat_assignments_meter_id ON cat_assignments(meter_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_wqx_biohabphys_location_id ON wqx_biohabphys(monitoring_location_id)"))
            
            conn.commit()
            
        logger.info("Additional database tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating additional database tables: {e}")
        return False

if __name__ == "__main__":
    create_additional_tables()

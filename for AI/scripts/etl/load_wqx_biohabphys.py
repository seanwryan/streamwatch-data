#!/usr/bin/env python3
"""
Load WQX biohabphys data from 2024 TWI WQX Submission.xlsx
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_wqx_biohabphys():
    """Load WQX biohabphys data from Excel file"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Loading WQX biohabphys data...")
        
        # Read Excel file
        file_path = 'data/raw/2024 TWI WQX Submission.xlsx'
        df = pd.read_excel(file_path, sheet_name='WQX biohabphys')
        
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Clean the data - remove completely empty rows
        df = df.dropna(how='all')
        
        # Convert date columns
        date_columns = ['Activity Start Date', 'Analysis Start Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert time columns
        time_columns = ['Activity Start Time']
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.time
        
        # Convert numeric columns
        numeric_columns = [
            'Activity Depth/Height Measure', 'Collection Area Measure', 'Collection Duration Measure',
            'Gear Procedure Unit Measure', 'Reach Length Measure', 'Reach Width Measure',
            'Net Mesh Size Measure', 'Net Surface Area Measure', 'Boat Speed Measure',
            'Group Summary Weight Value', 'Proportion Sample Processed Numeric', 'Target Count',
            'Lower Class Bound', 'Upper Class Bound', 'Result Detection/Quantitation Limit Measure',
            'Result Depth/Height Measure'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert integer columns
        integer_columns = [
            'Result Sampling Point Place in Series Sampling Component Place in Series',
            'Group Summary Count'
        ]
        
        for col in integer_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        
        # Truncate string fields to match database schema
        string_columns = {
            'Project ID': 100, 'Monitoring Location ID': 50, 'Activity ID (CHILD-subset)': 100,
            'Activity ID User Supplied (PARENTs)': 100, 'Activity Type': 100, 'Activity Media Name': 100,
            'Activity Start Time Zone': 10, 'Activity Depth/Height Unit': 20, 'Assemblage Sampled Name': 100,
            'Habitat Selection Method': 100, 'Collection Area Unit': 20, 'Collection Duration Unit': 20,
            'Gear Procdure Unit Code': 20, 'Sampling Component Name': 100, 'Reach Length Unit': 20,
            'Reach Width Unit': 20, 'Sample Collection Method ID': 100, 'Sample Collection Method Context': 100,
            'Sample Collection Equipment Name': 100, 'Net Mesh Size Unit': 20, 'Net Type': 100,
            'Net Surface Area Unit': 20, 'Boat Speed Unit': 20, 'Characteristic Name': 100,
            'Characteristic Name User Supplied': 100, 'Method Speciation': 100, 'Result Detection Condition': 100,
            'Result Value': 100, 'Result Unit': 20, 'Result Sample Fraction': 100, 'Result Status ID': 50,
            'Statistical Base Code': 50, 'Result Value Type': 50, 'Result Weight Basis': 50,
            'Result Sampling Point Name': 100, 'Result Sampling Point Type': 100, 'Biological Intent': 100,
            'Biological Individual ID': 100, 'Subject Taxonomic Name': 200, 'Subject Taxonomic Name User Supplied': 200,
            'Unidentified Species ID': 100, 'Sample Tissue Anatomy': 100, 'Group Summary Weight Unit': 20,
            'Frequency Class Descriptor': 100, 'Frequency Class Descriptor Unit': 20, 'Taxon Cell Form': 100,
            'Taxon Cell Shape': 100, 'Taxon Habit': 100, 'Taxon Voltinism': 100, 'Taxon Pollution Tolerance': 100,
            'Taxon Pollution Tolerance Scale': 100, 'Taxon Trophic Level': 100, 'Taxon Functional Feeding Group': 100,
            'Result Analytical Method ID': 100, 'Result Analytical Method Context': 100,
            'Result Detection/Quantitation Limit Type': 100, 'Result Detection/Quantitation Limit Unit': 20,
            'Laboratory Name': 200, 'Taxon Citation ID': 100, 'Activity Group ID': 100, 'Activity Group Type': 100,
            'Activity Group Name': 100, 'Result Depth/Altitude Reference Point': 100, 'Result Depth/Height Unit': 20
        }
        
        for col, max_len in string_columns.items():
            if col in df.columns:
                df[col] = df[col].astype(str).str[:max_len]
        
        # Handle TEXT columns (no length limit)
        text_columns = [
            'Sample Collection Equipment Comment', 'Subject Taxonomic Name User Supplied Reference Text',
            'Result Comment', 'Result Sampling Point Comment Text'
        ]
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Rename columns to match database schema (lowercase with underscores)
        column_mapping = {
            'Project ID': 'project_id',
            'Monitoring Location ID': 'monitoring_location_id',
            'Activity ID (CHILD-subset)': 'activity_id_child',
            'Activity ID User Supplied (PARENTs)': 'activity_id_user_supplied',
            'Activity Type': 'activity_type',
            'Activity Media Name': 'activity_media_name',
            'Activity Start Date': 'activity_start_date',
            'Activity Start Time': 'activity_start_time',
            'Activity Start Time Zone': 'activity_start_time_zone',
            'Activity Depth/Height Measure': 'activity_depth_height_measure',
            'Activity Depth/Height Unit': 'activity_depth_height_unit',
            'Assemblage Sampled Name': 'assemblage_sampled_name',
            'Habitat Selection Method': 'habitat_selection_method',
            'Collection Area Measure': 'collection_area_measure',
            'Collection Area Unit': 'collection_area_unit',
            'Collection Duration Measure': 'collection_duration_measure',
            'Collection Duration Unit': 'collection_duration_unit',
            'Gear Procedure Unit Measure': 'gear_procedure_unit_measure',
            'Gear Procdure Unit Code': 'gear_procedure_unit_code',
            'Sampling Component Name': 'sampling_component_name',
            'Result Sampling Point Place in Series Sampling Component Place in Series': 'result_sampling_point_place_in_series',
            'Reach Length Measure': 'reach_length_measure',
            'Reach Length Unit': 'reach_length_unit',
            'Reach Width Measure': 'reach_width_measure',
            'Reach Width Unit': 'reach_width_unit',
            'Sample Collection Method ID': 'sample_collection_method_id',
            'Sample Collection Method Context': 'sample_collection_method_context',
            'Sample Collection Equipment Name': 'sample_collection_equipment_name',
            'Sample Collection Equipment Comment': 'sample_collection_equipment_comment',
            'Net Mesh Size Measure': 'net_mesh_size_measure',
            'Net Mesh Size Unit': 'net_mesh_size_unit',
            'Net Type': 'net_type',
            'Net Surface Area Measure': 'net_surface_area_measure',
            'Net Surface Area Unit': 'net_surface_area_unit',
            'Boat Speed Measure': 'boat_speed_measure',
            'Boat Speed Unit': 'boat_speed_unit',
            'Characteristic Name': 'characteristic_name',
            'Characteristic Name User Supplied': 'characteristic_name_user_supplied',
            'Method Speciation': 'method_speciation',
            'Result Detection Condition': 'result_detection_condition',
            'Result Value': 'result_value',
            'Result Unit': 'result_unit',
            'Result Sample Fraction': 'result_sample_fraction',
            'Result Status ID': 'result_status_id',
            'Statistical Base Code': 'statistical_base_code',
            'Result Value Type': 'result_value_type',
            'Result Weight Basis': 'result_weight_basis',
            'Result Sampling Point Name': 'result_sampling_point_name',
            'Result Sampling Point Type': 'result_sampling_point_type',
            'Biological Intent': 'biological_intent',
            'Biological Individual ID': 'biological_individual_id',
            'Subject Taxonomic Name': 'subject_taxonomic_name',
            'Subject Taxonomic Name User Supplied': 'subject_taxonomic_name_user_supplied',
            'Subject Taxonomic Name User Supplied Reference Text': 'subject_taxonomic_name_user_supplied_reference_text',
            'Unidentified Species ID': 'unidentified_species_id',
            'Sample Tissue Anatomy': 'sample_tissue_anatomy',
            'Group Summary Weight Value': 'group_summary_weight_value',
            'Group Summary Weight Unit': 'group_summary_weight_unit',
            'Group Summary Count': 'group_summary_count',
            'Proportion Sample Processed Numeric': 'proportion_sample_processed_numeric',
            'Target Count': 'target_count',
            'Frequency Class Descriptor': 'frequency_class_descriptor',
            'Frequency Class Descriptor Unit': 'frequency_class_descriptor_unit',
            'Lower Class Bound': 'lower_class_bound',
            'Upper Class Bound': 'upper_class_bound',
            'Taxon Cell Form': 'taxon_cell_form',
            'Taxon Cell Shape': 'taxon_cell_shape',
            'Taxon Habit': 'taxon_habit',
            'Taxon Voltinism': 'taxon_voltinism',
            'Taxon Pollution Tolerance': 'taxon_pollution_tolerance',
            'Taxon Pollution Tolerance Scale': 'taxon_pollution_tolerance_scale',
            'Taxon Trophic Level': 'taxon_trophic_level',
            'Taxon Functional Feeding Group': 'taxon_functional_feeding_group',
            'Result Analytical Method ID': 'result_analytical_method_id',
            'Result Analytical Method Context': 'result_analytical_method_context',
            'Analysis Start Date': 'analysis_start_date',
            'Result Detection/Quantitation Limit Type': 'result_detection_quantitation_limit_type',
            'Result Detection/Quantitation Limit Measure': 'result_detection_quantitation_limit_measure',
            'Result Detection/Quantitation Limit Unit': 'result_detection_quantitation_limit_unit',
            'Laboratory Name': 'laboratory_name',
            'Taxon Citation ID': 'taxon_citation_id',
            'Result Comment': 'result_comment',
            'Activity Group ID': 'activity_group_id',
            'Activity Group Type': 'activity_group_type',
            'Activity Group Name': 'activity_group_name',
            'Result Sampling Point Comment Text': 'result_sampling_point_comment_text',
            'Result Depth/Altitude Reference Point': 'result_depth_altitude_reference_point',
            'Result Depth/Height Measure': 'result_depth_height_measure',
            'Result Depth/Height Unit': 'result_depth_height_unit'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Clear existing data
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM wqx_biohabphys"))
            conn.commit()
        
        # Load data in batches (this is a large table)
        batch_size = 500
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('wqx_biohabphys', engine, if_exists='append', index=False, method='multi')
            logger.info(f"Loaded batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
        
        logger.info(f"Successfully loaded {total_rows} WQX biohabphys records")
        return True
        
    except Exception as e:
        logger.error(f"Error loading WQX biohabphys data: {e}")
        return False

if __name__ == "__main__":
    load_wqx_biohabphys()

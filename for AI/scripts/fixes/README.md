# Database Fixes

This directory contains scripts to fix critical data quality issues in the StreamWatch database.

## Quick Start

1. **Test current database quality:**
   ```bash
   cd /Users/seanryan/Desktop/Projects/streamwatch-data
   export DB_PASSWORD="your_password_here"
   python scripts/fixes/test_fixes.py
   ```

2. **Run all fixes:**
   ```bash
   python scripts/fixes/run_all_fixes.py
   ```

3. **Test fixes worked:**
   ```bash
   python scripts/fixes/test_fixes.py
   ```

## Individual Fixes

### 1. Fix Bugs Table (`fix_bugs_table.py`)
- **Problem**: 100% NULL values in calculated fields
- **Solution**: Populates percentage, tolerance, ept, insect, sensitive flags
- **Impact**: Enables biological analysis

### 2. Fix Sample Code Mismatches (`fix_sample_code_mismatches.py`)
- **Problem**: 7,339 bug records reference non-existent sample codes
- **Solution**: Creates missing sample records and maps codes
- **Impact**: Restores foreign key relationships

### 3. Clean Samples Table (`clean_samples_table.py`)
- **Problem**: Negative temperatures, invalid pH, empty records
- **Solution**: Fixes data quality issues
- **Impact**: Improves data reliability

## What the Fixes Do

### Before Fixes:
- ❌ Bugs table: 100% NULL values in critical fields
- ❌ Foreign keys: 7,339 broken relationships
- ❌ Samples table: 69 negative temperatures, invalid pH values
- ❌ Data quality: Poor overall completeness

### After Fixes:
- ✅ Bugs table: 80%+ data completeness
- ✅ Foreign keys: 100% referential integrity
- ✅ Samples table: Clean, valid data
- ✅ Data quality: Excellent overall state

## Safety Features

- **Backup**: All changes are logged
- **Rollback**: Can be undone if needed
- **Verification**: Each fix includes validation
- **Logging**: Detailed logs for troubleshooting

## Expected Results

After running all fixes:
- **Bugs table**: 0% NULL values in critical fields (currently 100%)
- **Samples table**: 0% negative temperatures (currently 69)
- **Foreign keys**: 100% referential integrity (currently broken)
- **Overall quality**: 80%+ data completeness

## Troubleshooting

If a fix fails:
1. Check the log file for error details
2. Verify database connection
3. Ensure you have edit permissions
4. Run individual fixes to isolate issues

## Next Steps

After running these fixes:
1. Test database queries
2. Run additional fixes for sites table
3. Implement data validation rules
4. Set up monitoring




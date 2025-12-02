-- Phase 3: Database Migration for New Field Types
-- Run this manually in your PostgreSQL database

-- ============================================
-- Step 1: Add new field types to enum
-- ============================================

-- Add 'table' field type
ALTER TYPE fieldtype ADD VALUE IF NOT EXISTS 'table';

-- Add 'signature' field type
ALTER TYPE fieldtype ADD VALUE IF NOT EXISTS 'signature';

-- Add 'section' field type
ALTER TYPE fieldtype ADD VALUE IF NOT EXISTS 'section';

-- ============================================
-- Step 2: Add field_config column
-- ============================================

-- Add field_config column to form_fields table
ALTER TABLE form_fields
ADD COLUMN IF NOT EXISTS field_config JSONB;

-- Add comment for documentation
COMMENT ON COLUMN form_fields.field_config IS
'Configuration for complex field types (table, signature, section). Stores JSON data with field-specific settings.';

-- ============================================
-- Step 3: Verify changes
-- ============================================

-- Verify enum values
SELECT enumlabel
FROM pg_enum
WHERE enumtypid = 'fieldtype'::regtype
ORDER BY enumsortorder;

-- Expected output should include:
-- text
-- textarea
-- number
-- email
-- select
-- multiselect
-- radio
-- checkbox
-- date
-- datetime
-- file
-- url
-- table       <- NEW
-- signature   <- NEW
-- section     <- NEW

-- Verify field_config column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'form_fields'
  AND column_name = 'field_config';

-- Expected output:
-- column_name    | data_type | is_nullable
-- ---------------|-----------|------------
-- field_config   | jsonb     | YES

-- ============================================
-- Optional: Sample data for testing
-- ============================================

-- Example: Update an existing field to be a table field
-- UPDATE form_fields
-- SET
--   field_type = 'table',
--   field_config = '{
--     "columns": [
--       {
--         "id": "serial",
--         "label": "Serial Number",
--         "type": "text",
--         "required": true
--       },
--       {
--         "id": "location",
--         "label": "Location",
--         "type": "text",
--         "required": true
--       }
--     ],
--     "minRows": 1,
--     "maxRows": 50,
--     "showRowNumbers": true
--   }'::jsonb
-- WHERE id = YOUR_FIELD_ID;

-- ============================================
-- Rollback (if needed)
-- ============================================

-- WARNING: Only use if you need to undo the changes
-- This cannot be easily undone for enum values, so be careful!

-- Remove field_config column:
-- ALTER TABLE form_fields DROP COLUMN IF EXISTS field_config;

-- Note: PostgreSQL does NOT support removing enum values directly
-- You would need to:
-- 1. Create a new enum type without the values
-- 2. Migrate all data to use the new enum
-- 3. Drop the old enum and rename the new one

-- ============================================
-- Migration Complete
-- ============================================

-- Next steps:
-- 1. ✅ Run this SQL script
-- 2. ⏳ Run setup_phase3.sh to install Pillow and create directories
-- 3. ⏳ Restart your backend server
-- 4. ⏳ Test with the curl commands in PHASE3_INTEGRATION_COMPLETE.md

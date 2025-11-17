# Quick Data Verification

## Current API Results

Based on the API response, here's what we're seeing:

### Total Records
- **API shows**: ~999-1000 total reprints
- **Verify in Supabase**: Count total rows in `BO_reprints` table

### Top Products
1. **Blanket**: 284 (28.4%)
2. **Calendar**: 280 (28.0%)
3. **Photobook-Photo Hardcover**: 149 (14.9%)
4. **Canvas**: 79 (7.9%)
5. **Mug**: 45 (4.5%)

**To verify**: In Supabase, group by `Product Type` and count - should match these numbers.

### Top Facilities
1. **FacilityB001**: 597 (59.7%)
2. **FacilityB046**: 210 (21.0%)
3. **FacilityB045**: 77 (7.7%)
4. **FacilityL029**: 59 (5.9%)

**To verify**: In Supabase, group by `ActualFacilityName` and count.

### Top Reasons (for Blankets)
1. **Fingerprint / Scuff Marks**: 200
2. **Lost in Transit**: 18
3. **Insufficient Address**: 15
4. **Colour Quality Is Poor**: 14
5. **Damaged in Transit**: 10

**To verify**: In Supabase, filter by `Product Type = "Blanket"`, then group by `Reprint Reason`.

---

## How to Verify in Supabase

### Method 1: Manual Count
1. Go to Supabase → Table Editor → `BO_reprints`
2. Check total row count (shown at bottom)
3. Should match API `total_reprints` (~999-1000)

### Method 2: SQL Query (More Accurate)
In Supabase SQL Editor, run:

```sql
-- Total count
SELECT COUNT(*) as total FROM "BO_reprints";

-- Top products
SELECT "Product Type", COUNT(*) as count
FROM "BO_reprints"
GROUP BY "Product Type"
ORDER BY count DESC
LIMIT 5;

-- Top facilities
SELECT "ActualFacilityName", COUNT(*) as count
FROM "BO_reprints"
GROUP BY "ActualFacilityName"
ORDER BY count DESC
LIMIT 5;

-- Top reasons for Blankets
SELECT "Reprint Reason", COUNT(*) as count
FROM "BO_reprints"
WHERE "Product Type" = 'Blanket'
GROUP BY "Reprint Reason"
ORDER BY count DESC
LIMIT 5;
```

Compare these results with the API output.

---

## What to Check

✅ **If numbers match**: Data is correct!
❌ **If numbers don't match**: 
- Check date filtering (API might be filtering by date)
- Check for null/empty values in Supabase
- Check Railway logs for warnings

---

## Quick Test

**Get all data (no date filter):**
```
https://reprint-production.up.railway.app/api/reprints/metrics
```

This should return the total count matching your Supabase table row count.


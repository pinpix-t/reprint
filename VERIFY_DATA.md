# How to Verify Your Data is Correct

## Quick Verification Steps

### 1. Check Total Count Matches Supabase

**In Supabase:**
1. Go to Supabase → Table Editor → `BO_reprints`
2. Count total rows (or check the row count at the bottom)

**In API:**
```
https://reprint-production.up.railway.app/api/reprints/metrics
```
Check `total_reprints` - should match (or be close if date filtered)

---

### 2. Check Date Range

**Test with different date ranges:**

**Last 30 days:**
```
https://reprint-production.up.railway.app/api/reprints/overview?days=30
```

**Last 90 days:**
```
https://reprint-production.up.railway.app/api/reprints/overview?days=90
```

**All data (last 2 years):**
```
https://reprint-production.up.railway.app/api/reprints/overview?days=730
```

The counts should increase as you widen the date range.

---

### 3. Verify Top Products

**Check in Supabase:**
1. Go to `BO_reprints` table
2. Group by `Product Type` column
3. Count occurrences

**Compare with API:**
```
https://reprint-production.up.railway.app/api/reprints/products
```

The top products should match what you see in Supabase.

---

### 4. Verify Top Facilities

**Check in Supabase:**
1. Group by `ActualFacilityName` column
2. Count occurrences

**Compare with API:**
```
https://reprint-production.up.railway.app/api/reprints/facilities
```

---

### 5. Verify Top Reasons

**Check in Supabase:**
1. Group by `Reprint Reason` column
2. Count occurrences

**Compare with API:**
```
https://reprint-production.up.railway.app/api/reprints/reasons
```

---

### 6. Check Railway Logs

Look for:
- "Fetched X raw records" - should match your table size
- "Processed X records" - should be the same
- "After date filter" - shows how many records match the date range
- Any warnings or errors

---

## Common Issues

### Issue 1: Counts Don't Match
- **Cause**: Date filtering is excluding data
- **Fix**: Use wider date range (`?days=730`)

### Issue 2: Top Products/Facilities Wrong
- **Cause**: Column name mismatch or data processing issue
- **Fix**: Check Railway logs for warnings

### Issue 3: Percentages Don't Add Up to 100%
- **Cause**: Only showing top N items, not all
- **Fix**: This is normal - percentages are of total, but only top items shown

---

## Manual Verification

1. **Pick a specific date range** from your Supabase data
2. **Count manually** in Supabase (use filters)
3. **Compare** with API response for same date range

Example:
- In Supabase: Filter `Requested date` between Oct 1-31, 2024
- Count rows manually
- In API: Use date parameters to match
- Compare counts

---

## What to Look For

✅ **Good signs:**
- Total count increases with wider date ranges
- Top products/facilities make sense
- Percentages are reasonable
- No errors in logs

❌ **Warning signs:**
- Counts are 0 when you know data exists
- Top items don't match Supabase
- Percentages are way off
- Errors in logs

---

## Quick Test

Run this to see all your data (no date filter):
```
https://reprint-production.up.railway.app/api/reprints/metrics
```

This should return the total count of ALL records in your table.


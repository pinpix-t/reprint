# Test Supabase Data Connection

## Quick Test Endpoint

To verify data is being fetched from Supabase, you can test this endpoint:

```
https://reprint-production.up.railway.app/api/reprints/metrics
```

This endpoint doesn't use date filters, so it should return ALL data from the table.

---

## Expected Behavior

**If data exists:**
- Should return `total_reprints` > 0
- Should show metrics

**If still 0:**
- Check Railway logs for errors
- Verify Supabase connection
- Check if table has data

---

## Debug Steps

1. **Test the metrics endpoint** (no date filter):
   ```
   https://reprint-production.up.railway.app/api/reprints/metrics
   ```

2. **Check Railway logs** for:
   - "No data returned from Supabase table BO_reprints"
   - "Returning X records after filtering"
   - Any error messages

3. **Verify Supabase table has data:**
   - Go to Supabase → Table Editor
   - Open `BO_reprints` table
   - Check row count

---

## If Metrics Endpoint Returns Data

Then the issue is with date filtering. The fix I just pushed should handle this.

---

## If Metrics Endpoint Still Returns 0

Then there's a different issue:
- Supabase connection problem
- Table is actually empty
- Column name mismatch
- Data processing error


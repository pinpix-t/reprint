# Supabase Table Names Configuration

## Answer: Supabase URL & Key Don't Change

✅ **Supabase URL** - Stays the same (database-level)
✅ **Supabase Key** - Stays the same (database-level)
❌ **Table Names** - These might need to match your actual tables

---

## Current Table Names in Code

The code is currently looking for these table names:

```python
REPRINT_TABLE = "reprints"
REVIEW_TABLE = "reviews"
```

**Location:** `backend/utils/db_access.py` (lines 23-24)

---

## If Your Tables Have Different Names

If your Supabase tables are named differently (e.g., `reprint_data`, `customer_reviews`), you need to update the code:

### Step 1: Check Your Supabase Table Names

1. Go to [supabase.com](https://supabase.com)
2. Open your project
3. Go to **Table Editor**
4. Note the exact table names

### Step 2: Update the Code

Edit `backend/utils/db_access.py`:

```python
# Change these to match your actual table names
REPRINT_TABLE = "your_actual_reprint_table_name"
REVIEW_TABLE = "your_actual_review_table_name"
```

### Step 3: Redeploy

After changing, redeploy Railway:
- Railway will auto-redeploy if connected to GitHub
- Or manually trigger a redeploy

---

## Column Names Also Matter

The code also expects specific column names. Check these in `backend/utils/db_access.py`:

```python
COLUMN_REQUESTED_DATE = "Requested date"
COLUMN_FACILITY_NAME = "ActualFacilityName"
COLUMN_PRODUCT_TYPE = "Product Type"
COLUMN_ORDER_NUMBER = "Order Number"
```

If your columns have different names, update these constants too.

---

## Quick Check

**Your Supabase credentials:**
- ✅ URL: `https://jqzpyztivqshzzsfdecp.supabase.co` (doesn't change)
- ✅ Key: Your anon key (doesn't change)

**What might be wrong:**
- ❌ Table name mismatch: Code looks for `reprints` but table is `reprint_data`
- ❌ Column name mismatch: Code looks for `Requested date` but column is `request_date`

---

## How to Verify

1. **Check Supabase Table Editor:**
   - What are your table names?
   - What are your column names?

2. **Check the Code:**
   - `backend/utils/db_access.py` lines 23-28
   - Do they match?

3. **Test the Connection:**
   - Railway logs should show if tables are found
   - Check Railway → Your Service → Logs

---

## Common Issues

**"Table not found" errors:**
→ Table names don't match

**"Column not found" errors:**
→ Column names don't match

**No data showing:**
→ Tables exist but might be empty, or column names don't match


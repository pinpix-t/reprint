# Debug: Website Shows All Zeros

## The Problem
✅ Frontend is connected to backend
✅ API is responding
❌ All data shows as 0

This means the Supabase query is returning empty results.

---

## Possible Causes

### 1. Table is Empty
- Check if `BO_reprints` table has any data in Supabase

### 2. Date Column Mismatch
- Code looks for column: `"Requested date"`
- Your table might have different column name
- Check your Supabase table column names

### 3. Date Format Issue
- Dates might not be in the format the code expects
- Code filters by date range (last 7 days by default)
- If dates are old or in wrong format, nothing matches

### 4. Column Name Mismatches
Code expects these columns:
- `"Requested date"` - for date filtering
- `"ActualFacilityName"` - for facility name
- `"Product Type"` - for product type
- `"Order Number"` - for order matching

---

## How to Debug

### Step 1: Check Railway Logs
1. Go to Railway → Your Service → **Logs**
2. Look for errors when API is called
3. Check for messages like:
   - "No data from Supabase"
   - "Error fetching reprints"
   - "Column not found"

### Step 2: Test API Directly
Test these URLs in your browser:

**Get all data (no date filter):**
```
https://reprint-production.up.railway.app/api/reprints/overview?days=365
```
(Use 365 days to see if there's any data at all)

**Test without date filter:**
```
https://reprint-production.up.railway.app/api/reprints/metrics
```
(No date parameters - should return all data)

### Step 3: Check Supabase Table
1. Go to Supabase → Table Editor
2. Open `BO_reprints` table
3. Check:
   - Does it have rows?
   - What are the column names?
   - What format are the dates in?

### Step 4: Check Column Names
Compare your Supabase columns with what the code expects:

**Code expects:**
- `Requested date`
- `ActualFacilityName`
- `Product Type`
- `Order Number`

**Your table might have:**
- `requested_date` (lowercase, underscore)
- `RequestedDate` (no space)
- `request_date` (different name)
- etc.

---

## Quick Fixes

### Fix 1: Update Column Names in Code
If your column names are different, update `backend/utils/db_access.py`:

```python
COLUMN_REQUESTED_DATE = "your_actual_column_name"
COLUMN_FACILITY_NAME = "your_actual_facility_column"
COLUMN_PRODUCT_TYPE = "your_actual_product_column"
COLUMN_ORDER_NUMBER = "your_actual_order_column"
```

### Fix 2: Test Without Date Filter
Temporarily remove date filtering to see if data exists:

Edit `backend/api/reprints.py` line 199-200:
```python
# Temporarily use a wider date range
end_date = datetime.now()
start_date = end_date - timedelta(days=365)  # Changed from days=days
```

### Fix 3: Check Date Format
If dates are stored as strings, they might need different parsing.
Check `backend/utils/data_processor.py` - the `parse_date` function.

---

## What to Check First

1. **Railway Logs** - Look for errors
2. **Supabase Table** - Does it have data?
3. **Column Names** - Do they match?
4. **Date Range** - Try `?days=365` to see if older data shows

---

## Tell Me

1. Does your `BO_reprints` table have data in Supabase?
2. What are the exact column names in your table?
3. What do Railway logs show when you call the API?
4. Does `?days=365` return any data?

This will help me pinpoint the exact issue!


# Export Variants Inventory to CSV

This repository contains a Python script `export_variants_inventory_to_csv` that exports Shopify product variants inventory data into a CSV file.

## Why This Exists

The function provides an automated way to export Shopify variant inventory data, including SKU, quantity, regular price, sale price, and a direct URL to the variant. It supports handling large inventories with Shopify GraphQL pagination.

## How It Works

1. **CSV Generation:**
   - Exports variant data into a CSV file named `inventory_variants_<timestamp>.csv` stored in the `./public/` directory.
   - Fields include SKU, inventory quantity, regular price, sale price, and a direct Shopify URL for each variant.

2. **Pagination & Throttling:**
   - The function handles Shopify GraphQL pagination, fetching 245 variants per query.
   - Throttles API requests based on the available API credits (`request_cost` and `restore_rate`), ensuring compliance with Shopify's rate limits.

3. **Error Handling & Retrying:**
   - Automatically retries on HTTP 429 (rate limit exceeded) or 502 errors.
   - Logs errors for easier debugging.

4. **Tracking Progress:**
   - Tracks the status and the total number of variants exported.
   - Provides console output for the progress and completion of the task.

## Example Usage

```python
export_variants_inventory_to_csv()
```

#### 5. run the main.py file

### YAML
The YAML file defines the GitHub Actions workflow to automate generating and pushing an inventory CSV file to a repository at regular intervals, as well as on pushes to the repository
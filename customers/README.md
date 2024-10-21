# Customer ID by Metafield

This repository contains a Python script `customer_id_by_metafield` that retrieves a Shopify customer ID (`gid`) and legacy ID using a specific metafield value. 

## Why This Exists

Shopify does not provide a direct way to query customers by metafield values. This function works around this limitation by using the `customerSegmentMembers` GraphQL query.

## How It Works

1. **Inputs:**
   - `metafield_namespace`: The namespace of the metafield.
   - `metafield_key`: The key of the metafield.
   - `metafield_value`: The value to query for.

2. **Process:**
   - Sends a GraphQL query to retrieve customers with matching metafield values.
   - Parses the response and returns the customer `gid` and legacy ID if found.

3. **Outputs:**
   - `customer_gid`: Shopify global ID.
   - `customer_legacy_id`: Legacy ID (numeric).
   - `status`: HTTP status code.
   - `message`: Response message.

## Error Handling

The function handles common HTTP errors (500, 429, 502) and logs detailed error messages for debugging.

## Example Usage

```python
response = customer_id_by_metafield("custom", "id__", "123456")
print(response["customer_gid"])

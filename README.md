# Shopify Inventory Automation Scripts

This repository contains automation scripts designed to interact with Shopify's GraphQL API to manage and export data related to customer information, product variant inventory and so on.

## Overview

The scripts in this repository allow for:

1. **Customer Data Retrieval:**
   - Fetch customer information based on specific metafield values.

2. **Product Variant Inventory Export:**
   - Export product variant details such as SKU, inventory quantity, regular price, and sale price into a CSV file.
   - Handles pagination and Shopify API rate limits efficiently.

## Key Features

- **Automated Data Fetching:** Scripts are designed to automatically retrieve and process data from a Shopify store.
- **CSV Export:** Product variant inventory data can be exported in a CSV format for easy reporting and analysis.
- **API Throttling Handling:** Includes functionality to respect Shopify API rate limits, ensuring efficient and compliant data fetching.
- **Error Handling:** Built-in mechanisms to handle common API errors and retry on failure.

## Usage

1. **Customer Data Script:**
   - Retrieves customer data using metafields from the Shopify store.

2. **Inventory Export Script:**
   - Exports product variant inventory data to a CSV file for inventory management purposes.

These scripts are designed for use with Shopify stores, providing essential automation for customer and product data management.

---

This repository offers scalable and efficient solutions for automating Shopify customer data retrieval and inventory export tasks.

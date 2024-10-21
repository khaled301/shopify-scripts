# Export inventory data from Shopify store

#### 1. Create a custom application in shopify admin to get the store credentials (API token)
https://admin.shopify.com/store/example-demo/settings/apps/development

#### 2. Install python-dotenv 
```
pip install python-dotenv
```

#### 3. create a .env file and add the following store credentials [#1]
```
SHOPIFY_STORE_NAME=example-demo
SHOPIFY_API_TOKEN=shpat_example_token
SHOPIFY_API_VERSION=2024-10
```

#### 4. create a directory called "public" to store the CSV

#### 5. run the main.py file

### Generate Inventory CSV YAML
#### The YAML file defines the GitHub Actions workflow to automate generating and pushing an inventory CSV file to a repository at regular intervals, as well as on pushes to the repository
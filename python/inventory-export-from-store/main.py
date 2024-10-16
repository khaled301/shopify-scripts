import os
# install python-dotenv 
from dotenv import load_dotenv
import csv
import time
import json
from datetime import datetime
import requests

# Load the .env file
load_dotenv()

def get_store_creds():
    store_name = os.getenv('SHOPIFY_STORE_NAME')
    store_token = os.getenv('SHOPIFY_API_TOKEN')
    store_version = os.getenv('SHOPIFY_API_VERSION')

    if not store_name or not store_token or not store_version:
        raise ValueError("Shopify store credentials are missing in the .env file")

    return {
        'store_name': store_name,
        'store_token': store_token,
        'version': store_version
    }

def sleep(seconds):
    time.sleep(seconds)

def get_date_time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def shopify_gql_request(store, query):
    headers = {
        "Content-Type": "application/graphql",
        "X-Shopify-Access-Token": store['store_token']
    }
    url = f"https://{store['store_name']}.myshopify.com/admin/api/{store['version']}/graphql.json"
    response = requests.post(url, data=query, headers=headers)
    return response.json()

def export_variants_inventory_to_csv():
    try:
        print(f"---***--- Inventory CSV generation task running ---***---")

        public_folder = "./public/"
        exported_file_name = f"inventory_variants.csv"
        final_path_file = f"{public_folder}{exported_file_name}"

        # CSV writing setup
        with open(final_path_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ 'SKU', 'Quantity', 'Regular Price', 'Sale Price', 'Variant URL'])

            is_continue = True
            cursor = None
            
            # To track progress of the operation
            progress = {
                'status': 'retrieving variants',
                'total_variant_count': 0,
                'completed': False,
                'started': get_date_time_now(),
                'ended': None
            }

            variant_count = 0
            
            # Shopify API request cost and restore rate | please adjust according to the desired store
            request_cost = 150
            restore_rate = 50

            while is_continue:
                query = f"""
                {{
                    productVariants(first: 200, {f'after: "{cursor}", ' if cursor else ''}) {{
                        pageInfo {{
                            hasNextPage
                        }}
                        edges {{
                            cursor
                            node {{
                                legacyResourceId
                                sku
                                inventoryQuantity
                                price
                                product {{
                                    legacyResourceId
                                    salePriceMetafieldValue: metafield(namespace: "custom", key: "sale_price") {{
                                        value
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
                """

                store_creds = get_store_creds()
                shopify_response = shopify_gql_request(store_creds, query)
                data = shopify_response.get('data')
                extensions = shopify_response.get('extensions')
                status = shopify_response.get('status')
                gql_errors = shopify_response.get('errors')
                
                print(shopify_response)
                print(data)
                print(extensions)
                print(status)

                if status in [429, 502]:
                    print(f"Error ==> Retrying in 5s... StatusCode: {status}")
                    sleep(5)
                    continue

                if data:
                    variants = data['productVariants']
                    
                    if not variants['pageInfo']['hasNextPage']:
                        is_continue = False

                    cursor = variants['edges'][-1]['cursor']
                    variant_count += len(variants['edges'])

                    for edge in variants['edges']:
                        node = edge['node']
                        writer.writerow([
                            node['sku'],
                            node['inventoryQuantity'],
                            node['price'],
                            node['product']['salePriceMetafieldValue']['value'] if node['product']['salePriceMetafieldValue'] else '',
                            f"https://{store_creds['store_name']}.myshopify.com/admin/products/{node['product']['legacyResourceId']}/variants/{node['legacyResourceId']}"
                        ])

                    progress['total_variant_count'] += variant_count
                else:
                    sleep(5)

                if extensions and extensions['cost']:
                    request_cost = extensions['cost']['requestedQueryCost']
                    restore_rate = extensions['cost']['throttleStatus']['restoreRate'] or 50

                if extensions and extensions['cost']['throttleStatus']['currentlyAvailable'] <= request_cost:
                    wait_ms = 1000 * (request_cost - extensions['cost']['throttleStatus']['currentlyAvailable']) / restore_rate
                    print(f"Sleeping for {wait_ms / 1000}s to restore credits")
                    sleep(wait_ms / 1000)

            progress['status'] = 'done'
            progress['completed'] = True
            progress['ended'] = get_date_time_now()

        print(progress)
        print(f"---*DONE*--- Inventory CSV export done---*DONE*---")
    except Exception as e:
        print(f"ERROR--- export_inventory_of_variants_to_csv ---ERROR => {str(e)}")


# call the export variants inventory function
export_variants_inventory_to_csv()

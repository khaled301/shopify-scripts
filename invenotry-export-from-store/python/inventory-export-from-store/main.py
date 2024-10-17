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
        raise ValueError("Shopify store credentials are missing")

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
    try:
        headers = {
            "Content-Type": "application/graphql",
            "X-Shopify-Access-Token": store['store_token']
        }
        url = f"https://{store['store_name']}.myshopify.com/admin/api/{store['version']}/graphql.json"
        response = requests.post(url, data=query, headers=headers)
        
        return {
            "status": response.status_code,
            "data": response.json()
        }
    except Exception as e:
        print(f"ERROR--- Shopify GQL Request ---ERROR => {str(e)}")
        
        return {
            "status": 500,
            "data": None
        }

def export_variants_inventory_to_csv():
    try:
        print(f"---***--- Inventory CSV generation task running ---***---")

        final_path_file = f"./public/inventory_variants_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        variant_count = 0
        
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
            
            # Shopify API request cost and restore rate | please adjust according to the desired store
            request_cost = 150
            restore_rate = 50

            while is_continue:
                query = f"""
                {{
                    productVariants(first: 245, {f'after: "{cursor}", ' if cursor else ''}) {{
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
                shopify_response_data = shopify_gql_request(store_creds, query)
                status = shopify_response_data["status"]
                shopify_response = shopify_response_data["data"]
                data = shopify_response.get('data')
                extensions = shopify_response.get('extensions')
                gql_errors = shopify_response.get('errors')
                
                # print(shopify_response)
                # print(data)
                # print(extensions)
                # print(status)
                
                if status in [500]:
                    print(f"Error ==> Something went wrong. Couldn't retrieve data from the store. StatusCode: {500}")
                    is_continue = False
                    continue

                if status in [429, 502]:
                    print(f"Error ==> Retrying in 5s... StatusCode: {status}")
                    sleep(5)
                    continue

                if data:
                    variants = data['productVariants']
                    
                    if not variants['pageInfo']['hasNextPage']:
                        is_continue = False

                    cursor = variants['edges'][-1]['cursor']

                    for edge in variants['edges']:
                        variant_count += 1
                        node = edge['node']
                        writer.writerow([
                            node['sku'],
                            node['inventoryQuantity'],
                            node['price'],
                            node['product']['salePriceMetafieldValue']['value'] if node['product']['salePriceMetafieldValue'] else '',
                            f"https://{store_creds['store_name']}.myshopify.com/admin/products/{node['product']['legacyResourceId']}/variants/{node['legacyResourceId']}"
                        ])

                    progress['total_variant_count'] = variant_count
                else:
                    sleep(1)

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

        print(f'Total Variant Count ====> {progress['total_variant_count']}')
        # print(progress)
        print(f"---*DONE*--- Inventory CSV export done---*DONE*---")
    except Exception as e:
        print(f"ERROR--- export_inventory_of_variants_to_csv ---ERROR => {str(e)}")


# call the export variants inventory function
export_variants_inventory_to_csv()

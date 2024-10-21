import os
from dotenv import load_dotenv
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

def customer_id_by_metafield(metafield_namespace, metafield_key, metafield_value):
    try:
        customer_gid = None
        customer_legacy_id = None
        response_message = "Sorry, couldn't retrieve customer data from the store."
        
        query = f"""
        {{
            customerSegmentMembers( query: "metafields.{f'{metafield_namespace}'}.{f'{metafield_key}'} = '{f'{metafield_value}'}' ", first: 1 ) {{
                edges {{
                    node {{
                        id
                        metafield(namespace:"custom", key:"id__") {{
                            value
                        }}
                    }}
                }}
            }}
        }}
        """

        store_creds = get_store_creds()
        gql_response = shopify_gql_request(store_creds, query)
        status = gql_response["status"]
        data = gql_response["data"].get('data')
        
        if status in [500, 429, 502]:
            print(f"Error ==> Something went wrong. Couldn't retrieve customer data from the store. StatusCode: {status}")
        
        if data:
            customer_segments = data['customerSegmentMembers']
            
            for edge in customer_segments['edges']:
                fetched_customer_metafield_value = edge['node']['metafield']['value']
                
                if fetched_customer_metafield_value == metafield_value and edge['node']['id']:
                    customer_legacy_segment_id = edge['node']['id']
                    customer_legacy_id = customer_legacy_segment_id.split('/')[-1] if customer_legacy_segment_id else  None
                    customer_gid = f"gid://shopify/Customer/{customer_legacy_id}" if customer_legacy_id else  None
                    response_message = "ok" if customer_gid else response_message
                    break
                
            status = 404 if not customer_gid else status
        else:
            print(f"Error ==> Something went wrong. No customer data found!")
        
        return {
            "status": status,
            "message": response_message,
            "customer_gid": customer_gid,
            "customer_legacy_id": customer_legacy_id
        }

    except Exception as e:
        print(f"ERROR--- customer_id_by_metafield ---ERROR => {str(e)}")
        return {
            "status": 500,
            "message": f"{str(e)}",
            "customer_gid": None,
            "customer_legacy_id": None
        }

# get customer gid by metafield
metafield_namespace = 'custom' # replace with customer metafield namespace
metafield_key = 'id__' # replace with customer metafield key
metafield_value = '33259' # replace with customer metafield value
customer_gid = customer_id_by_metafield(metafield_namespace, metafield_key, metafield_value)
print(customer_gid)

import os
import requests
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# define graphql endpoint
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# query to find recent orders
query = """
    query GetRecentOrders ($startDate: Date!, $endDate: Date!) {
        allOrders(startDate: $startDate, endDate: $endDate) {
            edges {
                node {
                    id
                    customer{
                    email
                    }
                }
            }
        """

def send_reminders():
    """
        Queries recent orders and logs reminders
    """
    # create a graphql client
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # calculate the date range for the past 7 days

    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    #define query var
    vars = {
        "startDate": seven_days_ago.isoformat(),
        "endDate": today.isoformat(),
    }

    try : 
        response = client.execute(GRAPHQL_ENDPOINT, json={
            'query': query,
            'variables': vars,
        })

        response.raise_for_status() #raise http error for bad requests
        data=response.json().get('data', {})

        orders = data.get('allOrders', {}).get('edges', [])

        log_file_path = "/tmp/order_reminders_log.txt"

        with open(log_file_path, 'a') as log_file:
            log_file.write(f"\n--- Reminders Processed at {datetime.now()} ---\n")
            if orders:
                for edge in orders:
                    order = edge['node']
                    order_id = order.get('id')
                    customer_email = order.get('customer', {}).get('email')
                    log_entry = f"Order ID: {order_id} for customer email {customer_email}"
                    log_file.write(log_entry + "\n")
            else:
                log_file.write("No recent orders found to process\n")
        print ("Order reminders processed successfully")
    except requests.exceptions.RequestException as e:
        print (f"Error connecting to GraphQL endpoint: {e}")
    except Exception as e:
        print (f"Error processing reminders: {e}")
if __name__ == "__main__":
    send_reminders()
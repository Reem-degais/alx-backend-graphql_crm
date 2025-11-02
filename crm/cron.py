import datetime
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Log a heartbeat to file and queries the GraphQL endpoint
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[$TIMESTAMP] CRM is alive\n"

    # append the hearbeat message to log file
    log_file_path = "/tmp/crm_heartbeat_log.txt"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_message)

    # verify the GraphQL endpoint is reachable
    graphql_endpoint = "http://localhost:8000/graphql"
    query = "{ hello }"

    try:
        transport = RequestsHTTPTransport(url=graphql_endpoint)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        response = client.execute(graphql_endpoint, json={"query": query})
        response.raise_for_status()  # raise http error for bad requests
        data = response.json().get("data", {})
        print("GraphQL endpoint is reachable and healthy")
    except Exception as e:
        print(f"Error querying GraphQL endpoint failed: {e}")


def update_low_stock():
    """
    Executes a GraphQL mutation to update low-stock products.
    """
    graphql_endpoint = "http://localhost:8000/graphql"
    mutation_query = """
        mutation {
          updateLowStockProducts {
            updatedProducts {
              name
              stock
            }
            message
          }
        }
    """

    try:
        transport = RequestsHTTPTransport(url=graphql_endpoint)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        response = client.execute(graphql_endpoint, json={"query": mutation_query})
        response.raise_for_status()
        data = response.json().get("data", {})

        if "updateLowStockProducts" in data:
            result = data["updateLowStockProducts"]
            updated_products = result.get("updatedProducts", [])
            message = result.get("message", "No message received.")

            log_file_path = "/tmp/low_stock_updates_log.txt"
            with open(log_file_path, "a") as f:
                f.write(f"\n--- Stock Update at {datetime.datetime.now()} ---\n")
                f.write(f"{message}\n")
                for product in updated_products:
                    f.write(
                        f"Updated product: {product['name']}, New stock: {product['stock']}\n"
                    )

        print(f"Low stock update processed. Message: {message}")

    except Exception as e:
        print(f"Failed to connect to GraphQL endpoint: {e}")
        print(f"An unexpected error occurred: {e}")
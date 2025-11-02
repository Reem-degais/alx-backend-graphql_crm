import requests
from celery import shared_task
from datetime import datetime
@shared_task
def generate_crm_report():
    graphql_endpoint = "http://localhost:8000/graphql"
    query = """
        query {
          allCustomers { totalCount }
          allOrders { totalCount }
        }
    """

    try:
        response = requests.post(graphql_endpoint, json={"query": query})
        response.raise_for_status()
        data = response.json().get("data", {})

        customer_count = data.get('allCustomers', {}).get('totalCount', 0)
        order_count = data.get('allOrders', {}).get('totalCount', 0)
        
        total_revenue = "N/A"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_log = f"{timestamp} - Report: {customer_count} customers, {order_count} orders, {total_revenue} revenue."

        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(report_log + '\n')
        
        return f"Report generated: {report_log}"

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to GraphQL endpoint: {e}")
        return f"Failed to generate report: {e}"
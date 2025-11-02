#!/bin/bash

# navigate to project root
cd ../..

# set timestamp
TIMESTAMP=$(date + "%Y-%m-%d %H:%M:%S")

DELETED_COUNT=$(./manage.py shell -c "
from django.utils import timezone 
from datetime import timedelta
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(order__order__date__gte=one_year_ago).distinct()
deleted_count, _ = inactive_customers.delete()

print(f"Successfully deleted {deleted_count} inactive customers.")
")

#log result 
echo "[$TIMESTAMP] total deleted $DELETED_COUNT accounts" >> /tmp/customer_cleanup_log.txt
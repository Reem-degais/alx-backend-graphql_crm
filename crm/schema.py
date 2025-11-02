import graphene
import re
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.utils import timezone

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

class CustomerType(DjangoObjectType):
    """
    Define customer's filds
    """
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    """
    Define Product fields
    """

    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    """
    Define Order fields
    """
    
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount")

class CustomerInput(graphene.InputObjectType):
    """
    Define Customer input fields
    """ 
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class  BulkCreateCustomersInput(graphene.InputObjectType):
    """
    Define BulkCreateCustomers input fields
    """

    customers = graphene.List(CustomerInput, required=True)

class ProductInput(graphene.InputObjectType):
    """
    Define product input fields
    """
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)

class CreateCustomer(graphene.Mutation):
    """
    Define CreateCustomer fields
    """
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        input = CustomerInput(required=True)

    def mutate(self, info, input = None):
        """
        Create a new customer
        """
        # Unique email verification
        if Customer.objects.filter(email=input.email).exists():
            return CreateCustomer(customer=None, message="Email already exists.")
        
        # phone format verification
        if input.phone:
            pattern = r"^\+?\d[\d\-]{7,15}$"  
            if not re.match(pattern, input.phone):
                return CreateCustomer(customer=None, message="Invalid phone number format.")
        
        # create and save a customer
        customer= Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully!")
    
class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    def mutate(self, info, input = None):
        created_customers = []
        errors = []

        for index, cust_input in enumerate(input):
            try:
                # Unique email verification
                if Customer.objects.filter(email=cust_input.email).exists():
                    errors.append(f"Customer at index {index} has duplicate email: {cust_input.email}")
                    continue

                # phone format verification
                if cust_input.phone:
                    pattern = r"^\+?\d[\d\-]{7,15}$"
                    if not re.match(pattern, cust_input.phone):
                        errors.append(f"Customer at index {index} has invalid phone: {cust_input.phone}")
                        continue

                # create and save a customer
                customer = Customer.objects.create(
                    name=cust_input.name,
                    email=cust_input.email,
                    phone=cust_input.phone
                )
                created_customers.append(customer)

            except Exception as e:
                errors.append(f"Customer at index {index} error: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    error = graphene.String()

    class Arguments:
        input = ProductInput(required=True)

    

    def mutate(self, info, input):
        # check price is positive and stock is not negative.
        if input.price <= 0:
            return CreateProduct(product=None, success=False, error="Price must be positive.")
        if input.stock < 0:
            return CreateProduct(product=None, success=False, error="Stock cannot be negative.")

        # create and save a product 
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock
        )

        return CreateProduct(product=product, success=True, error=None)

class CreateOrder(graphene.Mutation):
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    error = graphene.String()

    class Arguments:
        input = OrderInput(required=True)

    

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, success=False, error="Invalid customer ID.")

        if not input.product_ids or len(input.product_ids) == 0:
            return CreateOrder(order=None, success=False, error="At least one product must be selected.")

        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            return CreateOrder(order=None, success=False, error="One or more product IDs are invalid.")

    
        total_amount = sum([p.price for p in products])

        order = Order.objects.create(
            customer=customer,
            order_date=input.order_date or timezone.now(),
            total_amount=total_amount
        )

        order.products.set(products)

        return CreateOrder(order=order, success=True, error=None)
    
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
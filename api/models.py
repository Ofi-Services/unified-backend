from django.db import models
from .constants import ACTIVITY_CHOICES

#The models are the representations of the database tables. They are used to interact with the database.
class Case(models.Model):

    id = models.CharField(max_length=25, primary_key=True)
    order_date = models.DateTimeField()
    employee_id = models.CharField(max_length=25)
    branch = models.CharField(max_length=25)
    supplier = models.CharField(max_length=100)
    avg_time = models.FloatField(default=0)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivery = models.DateTimeField(null=True, blank=True)
    on_time = models.BooleanField(default=False)
    in_full = models.BooleanField(default=False)
    number_of_items = models.IntegerField()
    ft_items = models.IntegerField()
    total_price = models.IntegerField()


    def __str__(self):
        return f"Case {self.id} - Duration: {self.duration}"

class Activity(models.Model):
    """
    A model representing an activity related to a case.

    Attributes:
        id (int): The primary key for the activity.
        case (Case): The related case of the activity
        timestamp (datetime): The timestamp of the activity.
        name (str): The name of the activity, chosen from ACTIVITY_CHOICES.
        case_index (int): The index of the case, with a default value of 0.
        tpt (float): The time per task of the activity, with a default value of 0.
    """
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, related_name='activities', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=25)
    tpt = models.FloatField(default=0)
    user = models.CharField(max_length=25, default='None')
    user_type = models.CharField(max_length=25, default='None')
    automatic = models.BooleanField(default=False)
    rework = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.case.id} - {self.name} at {self.timestamp}"
    
class Variant(models.Model):
    """
    A model representing a variant.

    Attributes:
        id (int): The primary key for the variant.
        activities (str): The activities of the variant.
        cases (str): The cases of the variant.
        number_cases (int): The amount of cases of the variant.
        percentage (float): The percentage of cases the variant includes.
        avg_time (float): The average time per case of the variant.
    """
    id = models.AutoField(primary_key=True)
    activities = models.CharField(max_length=50)
    cases = models.CharField(max_length=50)
    number_cases = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    avg_time = models.FloatField(default=0)

    def __str__(self):
        return self.name
    

class Inventory(models.Model):
    """
    Inventory model represents the inventory of products in the system.
    Attributes:
        id (AutoField): The primary key for the inventory record.
        product_code (CharField): The code identifying the product. Can be blank or null.
        product_name (CharField): The name of the product.
        current_stock (IntegerField): The current stock level of the product.
        unit_price (IntegerField): The price per unit of the product.
    Methods:
        __str__(): Returns the string representation of the Inventory instance, 
                   which is the product code.
    """
    id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=255)
    current_stock = models.IntegerField()
    unit_price = models.IntegerField()
    new_product = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the string representation of the Inventory instance.
        """
        return f'{self.product_code}'

class OrderItem(models.Model):
    """
    OrderItem represents an item in an order, including details about the material, quantity, pricing, and related inventory suggestions.
    Attributes:
        order (ForeignKey): A reference to the associated Order. Deletes the OrderItem if the Order is deleted.
        material_name (CharField): The name of the material for the order item. Maximum length is 255 characters.
        material_code (CharField): An optional code for the material. Maximum length is 255 characters.
        quantity (IntegerField): The quantity of the material ordered.
        unit_price (IntegerField): The price per unit of the material.
        is_free_text (BooleanField): Indicates whether the material is a free-text entry.
        suggestion (ForeignKey): An optional reference to an Inventory item as a suggestion. Deletes the suggestion if the Inventory item is deleted.
        confidence (FloatField): An optional confidence score for the suggestion.
    Methods:
        __str__(): Returns a string representation of the OrderItem instance, including the material name and quantity.
    """
    order = models.ForeignKey(Case, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=255)
    material_code = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField()
    unit_price = models.IntegerField()
    is_free_text = models.BooleanField()
    suggestion = models.ForeignKey(Inventory, on_delete=models.CASCADE, blank=True, null=True, related_name='suggestion1_order_items')
    confidence = models.FloatField(blank=True, null=True)


    def __str__(self):
        """
        Returns the string representation of the OrderItem instance.
        """
        return f'{self.material_name} - {self.quantity}'

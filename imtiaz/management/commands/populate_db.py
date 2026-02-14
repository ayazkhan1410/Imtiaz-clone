from django.core.management.base import BaseCommand
from imtiaz.models import Category, Product


class Command(BaseCommand):
    help = "Populate the database with initial categories and products"

    def handle(self, *args, **options):
        # Add categories
        categories_data = [
            {"name": "Vegetables", "description": "Fresh and organic vegetables for daily needs."},
            {"name": "Meat", "description": "High-quality meat including chicken, beef, and mutton."},
            {"name": "Electrical Appliances", "description": "Modern and efficient home appliances."},
            {"name": "Groceries", "description": "Everyday essentials and household items."},
            {"name": "Fruits", "description": "Seasonal and fresh fruits directly from farms."},
            {"name": "Beverages", "description": "Refreshing drinks and beverages for all occasions."},
        ]
        
        categories = []
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"]}
            )
            categories.append(category)
        
        self.stdout.write(f"Added {len(categories)} categories.")
        
        # Add products
        products_data = [
            {
                "category": categories[0],
                "name": "Carrot",
                "description": "Fresh and crunchy carrots, perfect for salads and cooking.",
                "orignal_price": 200,
                "discount_percentage": 10,
                "is_available": True,
                "in_stock": 100,
            },
            {
                "category": categories[0],
                "name": "Potato",
                "description": "High-quality potatoes for all your cooking needs.",
                "orignal_price": 150,
                "discount_percentage": 5,
                "is_available": True,
                "in_stock": 200,
            },
            {
                "category": categories[1],
                "name": "Chicken Breast",
                "description": "Lean and fresh chicken breast, perfect for healthy meals.",
                "orignal_price": 500,
                "discount_percentage": 8,
                "is_available": True,
                "in_stock": 50,
            },
            {
                "category": categories[1],
                "name": "Beef Mince",
                "description": "Freshly minced beef for your favorite recipes.",
                "orignal_price": 700,
                "discount_percentage": 10,
                "is_available": True,
                "in_stock": 30,
            },
            {
                "category": categories[2],
                "name": "Microwave Oven",
                "description": "Efficient microwave oven with multiple cooking modes.",
                "orignal_price": 12000,
                "discount_percentage": 15,
                "is_available": True,
                "in_stock": 20,
            },
            {
                "category": categories[2],
                "name": "Electric Kettle",
                "description": "Fast boiling electric kettle, ideal for making tea and coffee.",
                "orignal_price": 3000,
                "discount_percentage": 10,
                "is_available": True,
                "in_stock": 25,
            },
            {
                "category": categories[3],
                "name": "Wheat Flour",
                "description": "Premium quality wheat flour for your everyday cooking needs.",
                "orignal_price": 800,
                "discount_percentage": 5,
                "is_available": True,
                "in_stock": 100,
            },
            {
                "category": categories[4],
                "name": "Apple",
                "description": "Fresh and juicy apples, perfect for snacking or baking.",
                "orignal_price": 300,
                "discount_percentage": 12,
                "is_available": True,
                "in_stock": 150,
            },
            {
                "category": categories[5],
                "name": "Orange Juice",
                "description": "Fresh and pulpy orange juice for a refreshing experience.",
                "orignal_price": 250,
                "discount_percentage": 10,
                "is_available": True,
                "in_stock": 200,
            },
        ]
        
        for data in products_data:
            product, created = Product.objects.get_or_create(
                category=data["category"],
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "orignal_price": data["orignal_price"],
                    "discount_percentage": data["discount_percentage"],
                    "is_available": data["is_available"],
                    "in_stock": data["in_stock"],
                },
            )
            self.stdout.write(f"Added product: {product.name}")

        self.stdout.write("Database population completed.")

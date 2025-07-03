import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


import json
from datetime import datetime
from pathlib import Path
from random import randint

from product.models import Category, Product, ProductDetails

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[1;36m"
NC = "\033[0m"

script_dir = Path(__file__).resolve().parent

# check if the database is already populated and if so exit silently
if Product.objects.get_queryset():
    print(f"{RED}Your database is already populated with data{NC}")
    choice = ""
    while choice != "y" and choice != "n":
        choice = input(
            "Are you sure you want to continue? (y, n) if yes it will only add missing default data: "
        )
        if choice == "n":
            exit(0)


with open(script_dir / "data.json", "r") as f:
    data = json.load(f)

# a set containing already existing categories
existing_categories = {c.name for c in Category.objects.get_queryset()}
existing_products = {p.name for p in Product.objects.get_queryset()}

count = 0
for prod in data:
    product_name = prod["name"]
    product_category = prod["category"]
    product_image = prod["image"]

    # Make a new category in the database if not already made
    if not product_category in existing_categories:
        cat = Category(name=product_category)
        cat.save()
        existing_categories.add(product_category)
    else:
        cat = Category.objects.get(name=product_category)

    if not product_name in existing_products:
        product = Product(name=product_name, image=product_image, category=cat)
        product.save()
        existing_products.add(product_name)
        count += 1
    else:
        continue

    # generate 1 to 5 random product details for each product
    # NOTE: for the same product we can't create more than one expiration date in product details
    # product: Milk, Expire Date: 2025-3-21, Quantity = 20
    # product: Milk, Expire Date: 2025-3-21, Quantity = 40 xxx
    dates = set()
    for i in range(randint(1, 5)):
        random_expire_year = randint(
            int(datetime.now().year), int(datetime.now().year) + randint(0, 3)
        )
        random_expire_month = (
            randint(
                int(datetime.now().month),
                int(datetime.now().month) + randint(0, 12),
            )
            % 13
        )
        random_expire_day = (
            randint(int(datetime.now().day), int(datetime.now().day) + randint(0, 30))
            % 29
        )
        random_expire_date = datetime(
            random_expire_year, random_expire_month or 1, random_expire_day or 1
        )

        # make sure while generating the random expiration dates that
        # nothing was repeated for the same product
        if random_expire_date in dates:
            continue
        else:
            dates.add(random_expire_date)
            product_details = ProductDetails(
                product=product,
                expire_date=random_expire_date,
                quantity=randint(10, 100),
            )
            product_details.save()

print(f"{GREEN}Created {count} products{NC}")

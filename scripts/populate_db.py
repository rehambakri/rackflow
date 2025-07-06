import os
import sys

import django

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "rackflow"))
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
existing_products = {p.name for p in Product.objects.get_queryset()}

ccount = 0
pcount = 0
pdcount = 0
for prod in data:
    product_name = prod["name"]
    product_category = prod["category"]
    product_image = prod["image"]

    category, res = Category.objects.get_or_create(name=product_category)
    ccount += int(res)
    product, res = Product.objects.get_or_create(
        name=product_name, image=product_image, category=category
    )
    pcount += int(res)

    seen_details = {detail.expire_date for detail in ProductDetails.objects.all()}
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
        if random_expire_date.date() in seen_details:
            continue
        seen_details.add((product.id, random_expire_date.date()))

        product_details, res = ProductDetails.objects.get_or_create(
            product=product,
            expire_date=random_expire_date,
            quantity=randint(10, 100),
        )
        pdcount += int(res)


print(f"{GREEN}Created {pcount} products{NC}")
print(f"{GREEN}Created {ccount} categories{NC}")
print(f"{GREEN}Created {pdcount} product_details{NC}")

######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestProductService
"""
import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, Product, Category, init_db
from tests.factories import ProductFactory
import json

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://localhost/test_products"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        # Já foi inicializado no __init__.py
        # init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_products(self, count):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(
                BASE_URL, json=test_product.serialize()
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(
            BASE_URL,
            json=test_product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

    def test_get_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)
        self.assertEqual(data["description"], test_product.description)
        self.assertEqual(Decimal(data["price"]), test_product.price)
        self.assertEqual(data["available"], test_product.available)
        self.assertEqual(data["category"], test_product.category.name)

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(
            BASE_URL,
            json=test_product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        new_product["description"] = "unknown"
        new_product["price"] = "99.99"
        new_product["available"] = False
        new_product["category"] = "TOOLS"
        response = self.client.put(
            f"{BASE_URL}/{new_product['id']}",
            json=new_product,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "unknown")
        self.assertEqual(Decimal(updated_product["price"]), Decimal("99.99"))
        self.assertEqual(updated_product["available"], False)
        self.assertEqual(updated_product["category"], "TOOLS")

    def test_delete_product(self):
        """It should Delete a Product"""
        products = self._create_products(5)
        product_count = self.get_product_count()
        test_product = products[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_by_name(self):
        """It should Query Products by Name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([p for p in products if p.name == test_name])
        response = self.client.get(
            BASE_URL,
            query_string=f"name={test_name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_by_category(self):
        """It should Query Products by Category"""
        products = self._create_products(5)
        test_category = products[0].category.name
        category_count = len([p for p in products if p.category.name == test_category])
        response = self.client.get(
            BASE_URL,
            query_string=f"category={test_category}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), category_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_query_by_availability(self):
        """It should Query Products by Availability"""
        products = self._create_products(5)
        test_available = products[0].available
        available_count = len([p for p in products if p.available == test_available])
        response = self.client.get(
            BASE_URL,
            query_string=f"available={str(test_available).lower()}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["available"], test_available)

    def test_list_by_availability(self):
        """It should List Products by Availability"""
        products = ProductFactory.create_batch(3)
        # Garante que apenas um produto tem a disponibilidade específica
        products[0].available = True
        products[1].available = False
        products[2].available = False
        for product in products:
            product.create()
        resp = self.client.get("/products?available=true")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["available"], True)

    def test_list_by_category(self):
        """It should List Products by Category"""
        products = ProductFactory.create_batch(3)
        # Garante que os produtos têm categorias diferentes
        products[0].category = Category.FOOD
        products[1].category = Category.TOOLS
        products[2].category = Category.CLOTHS
        for product in products:
            product.create()
        resp = self.client.get(f"/products?category={Category.FOOD.name}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], Category.FOOD.name)

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def get_product_count(self):
        """save the current number of products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("data = %s", data)
        return len(data)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.create()
        resp = self.client.get(f"/products/{product.id}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["name"], product.name)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.create()
        resp = self.client.put(
            f"/products/{product.id}",
            json=product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["id"], product.id)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        resp = self.client.delete(f"/products/{product.id}")
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()
        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)

    def test_list_by_name(self):
        """It should List Products by Name"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()
        resp = self.client.get(f"/products?name={products[0].name}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], products[0].name)

    def test_list_by_category(self):
        """It should List Products by Category"""
        products = ProductFactory.create_batch(3)
        # Garante que os produtos têm categorias diferentes
        products[0].category = Category.FOOD
        products[1].category = Category.TOOLS
        products[2].category = Category.CLOTHS
        for product in products:
            product.create()
        resp = self.client.get(f"/products?category={Category.FOOD.name}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], Category.FOOD.name)

    def test_list_by_availability(self):
        """It should List Products by Availability"""
        products = ProductFactory.create_batch(3)
        # Garante que apenas um produto tem a disponibilidade específica
        products[0].available = True
        products[1].available = False
        products[2].available = False
        for product in products:
            product.create()
        resp = self.client.get("/products?available=true")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["available"], True)

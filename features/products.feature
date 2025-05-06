Feature: The product store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name       | description     | price   | available | category  |
        | Hat       | A nice hat      | 12.99   | True      | CLOTHS    |
        | Shoes     | Running shoes   | 59.99   | True      | CLOTHS    |
        | Pants     | Blue jeans      | 34.99   | True      | CLOTHS    |
        | Shirt     | White t-shirt   | 14.99   | True      | CLOTHS    |
        | Socks     | Cotton socks    | 5.99    | True      | CLOTHS    |
        | Apples    | Red apples      | 2.99    | True      | FOOD      |
        | Bread     | Whole wheat     | 3.99    | True      | FOOD      |
        | Milk      | 2% milk        | 4.99    | True      | FOOD      |
        | Eggs      | Large eggs      | 3.99    | True      | FOOD      |
        | Cheese    | Cheddar cheese  | 7.99    | True      | FOOD      |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product Catalog Administration" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I set the "Description" to "A nice hat"
    And I set the "Price" to "12.99"
    And I select "True" in the "Available" dropdown
    And I select "CLOTHS" in the "Category" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A nice hat" in the "Description" field
    And I should see "12.99" in the "Price" field
    And I should see "True" in the "Available" dropdown
    And I should see "CLOTHS" in the "Category" dropdown

Scenario: List all products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the results
    And I should see "Shoes" in the results
    And I should see "Pants" in the results
    And I should see "Shirt" in the results
    And I should see "Socks" in the results
    And I should see "Apples" in the results
    And I should see "Bread" in the results
    And I should see "Milk" in the results
    And I should see "Eggs" in the results
    And I should see "Cheese" in the results

Scenario: Search for Cloths
    When I visit the "Home Page"
    And I select "CLOTHS" in the "Category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the results
    And I should see "Shoes" in the results
    And I should see "Pants" in the results
    And I should see "Shirt" in the results
    And I should see "Socks" in the results
    And I should not see "Apples" in the results
    And I should not see "Bread" in the results
    And I should not see "Milk" in the results
    And I should not see "Eggs" in the results
    And I should not see "Cheese" in the results

Scenario: Search for Food
    When I visit the "Home Page"
    And I select "FOOD" in the "Category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "Hat" in the results
    And I should not see "Shoes" in the results
    And I should not see "Pants" in the results
    And I should not see "Shirt" in the results
    And I should not see "Socks" in the results
    And I should see "Apples" in the results
    And I should see "Bread" in the results
    And I should see "Milk" in the results
    And I should see "Eggs" in the results
    And I should see "Cheese" in the results

Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A nice hat" in the "Description" field
    When I change "Name" to "Baseball Cap"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Baseball Cap" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Baseball Cap" in the results
    And I should not see "Hat" in the results

Scenario: Delete a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A nice hat" in the "Description" field
    When I press the "Delete" button
    Then I should see the message "Product has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "Hat" in the results

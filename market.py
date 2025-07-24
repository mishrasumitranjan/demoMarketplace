import os
import json
import sys
import pyfiglet
import time

from rich import print as rprint
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


# Define Class
class Market:
    """
    A class that creates a market object and handles the user and admin interaction.
    """
    def __init__(self):
        """
        Initialization of the instance. No input is required as everything required for operation is fetched from files
        or created during execution.
        """
        # Flags used to create temporary messages.
        self.flags = {"invalid_input": 0,
                      "first_entry": 1,
                      "added_to_cart": 0,
                      "removed_from_cart": 0,
                      "cart_cleared": 0,
                      "cart_empty": 0,
                      "item_added": 0,
                      "item_edited": 0,
                      "item_removed": 0,
                      "empty_category": 0}
        self.current_product = {}

        # Temporary variable to store the name of the empty category.
        self.empty_category = ""

        # Create an empty cart for the user.
        self.cart = []

        self.categories = []

        # Load stock data from stock.json.
        with open("stock.json") as file:
            self.stock = json.load(file)

        # Load user data from users.json.
        with open("users.json") as file:
            self.user_list = json.load(file)

        # Initial update of the list of categories from the stock.
        self.update_categories()
        self.user = self.get_user()
        if self.user["type"] == "user":
            self.cart = self.user["cart"]
            self.main_menu()
        elif self.user["type"] == "admin":
            self.admin_menu()

    def update_categories(self):
        """
        Update the list of categories from the stock.
        :return:
        """
        categories = [c["category"] for c in self.stock["Categories"]]
        self.categories = []
        for i in range(len(categories)):
            self.categories.append([str(i + 1), categories[i]])

    def update_stock(self):
        """
        Update the stock in the file.
        :return:
        """
        self.update_categories()
        with open('stock.json', 'w') as file:
            json.dump(self.stock, file, indent=4)

    def update_cart_in_file(self):
        """
        Update the cart in the file.
        :return:
        """
        for user in self.user_list["users"]:
            if user == self.user:
                user["cart"] = self.cart
        with open('users.json', 'w') as file:
            json.dump(self.user_list, file, indent=4)

    def get_user(self):
        """
        Get the current user from the list of users.
        :return:
        """
        wrong_pwd = no_user = 0
        print("Please enter your credentials. \n")
        while True:
            if wrong_pwd == 1:
                print("Password is incorrect.\n")
                wrong_pwd = 0
            elif no_user == 1:
                print("User not found.\n")
                no_user = 0
            username = input("Username: ")
            password = input("Password: ")
            for user in self.user_list["users"]:
                if username == user["username"]:
                    if password == user["password"]:
                        return user
                    else:
                        wrong_pwd = 1
                        break
            else:
                no_user = 1
            os.system("cls")

    def admin_menu(self):
        """
        Admin menu for managing items.
        :return:
        """
        while True:
            self.clear()
            print("Admin Menu")
            print("-" * (len("Admin Menu") + 1))
            actions = [["1", "View Items"], ["2", "Add Item"], ["3", "Edit Item"], ["4", "Remove Item"], ["5", "Exit"]]
            print(tabulate(actions, tablefmt="presto"))
            option = input("\nWhat would you like to do? ").strip()
            if option in actions[0]:
                self.view_items()
            elif option in actions[1]:
                self.flags["item_added"] = self.add_to_category()
            elif option in actions[2]:
                self.flags["item_edited"] = self.edit_in_category()
            elif option in actions[3]:
                self.flags["item_removed"] = self.remove_from_category()
            elif option in actions[4]:
                self.exit_market()
            else:
                self.flags["invalid_input"] = 1

    def view_items(self):
        """
        View all items in the stock in a tree structure.
        :return:
        """
        self.clear()
        product_tree = Tree(list(self.stock.keys())[0])
        for c in self.stock["Categories"]:
            node = product_tree.add(c["category"])
            for p in c["products"]:
                node.add(p["name"])
        rprint(product_tree)
        return input("Enter any option to return to the previous menu.")

    def add_to_category(self):
        self.clear()
        print("Add to Category")
        print("-" * (len("Add to Category") + 1))
        print(tabulate(self.categories, tablefmt="presto"))
        print("\nEnter 0 to return to previous menu.")
        option = input("Enter product category of new item: ")
        if option == "0":
            return 0
        if option == "X":
            self.exit_market()
        for c in self.categories:
            if option in c:
                return self.add_item(c[1])
        else:
            if option.isnumeric():
                self.flags["invalid_input"] = 1
                return 0
            rprint(f"The category [u]{option}[/u] is not present in the current stock.")
            chk = input("Do you want to create a new Category?(Y/N) ")
            if chk.strip().lower() == "y":
                # Adds a new category to stock with and empty list for products.
                self.stock["Categories"].append({"category": option, "products": []})
                return self.add_item(option)
            else:
                return 0

    def add_item(self, category):
        """
        Adds a new product to the specified category in stock
        :param category: Category name to add product to
        :return:
        """
        self.clear()
        title_string = f"Adding new product to {category} category"
        print(title_string)
        print("-" * (len(title_string) + 1))
        p_name = input("Enter Product Name: ").strip()
        p_details = input("\nEnter Product Details: ").strip()
        while True:
            try:
                p_rating = float(input("\nEnter Product Rating: ").strip())
                if p_rating <= 0:
                    print("Invalid Value. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid Value. Please try again.")

        while True:
            try:
                p_price = float(input("\nEnter Product Price: ").strip())
                if p_price <= 0:
                    print("Invalid Value. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid Value. Please try again.")
        print("")

        product_details = [
            ["Product Name", p_name],
            ["Product Details", p_details],
            ["Product Rating", p_rating],
            ["Product Price(₹)", p_price]
        ]
        print(tabulate(product_details, tablefmt="presto"))

        confirm = input(f"\nWould you like to add this product to {category} category?(Y/N) ").strip().lower()
        if confirm != "y":
            return 0

        self.current_product = {
            "name": p_name,
            "details": p_details,
            "rating": p_rating,
            "price": p_price,
            "colors": []
        }
        for c in self.stock["Categories"]:
            if category == c["category"]:
                c["products"].append(self.current_product)
        self.update_stock()
        return 1

    def edit_in_category(self):
        """
        Edit an item from a specific category.
        :return:
        """
        while True:
            self.clear()
            print("Edit in Category")
            print("-" * (len("Edit in Category") + 1))
            print(tabulate(self.categories, tablefmt="presto"))
            print("\nEnter 0 to return to previous menu.")
            option = input("Enter product category to edit item: ")
            if option == "0":
                return 0
            if option == "X":
                self.exit_market()
            for c in self.categories:
                if option in c:
                    return self.edit_this_item(c[1])
            else:
                self.flags["invalid_input"] = 1

    def edit_this_item(self, category):
        self.clear()
        main_string = f"Browsing Category: {category}"
        print(main_string)
        print("-" * (len(main_string) + 1))
        products = []
        counter = 1
        '''
        Old Code
        for c in self.stock["Categories"]:
            if c["category"] == category:
                for p in c["products"]:
                    products.append({"no.": counter,
                                     "name": p["name"],
                                     "rating": p["rating"],
                                     "price": p["price"]})
                    counter += 1
        '''

        c_products = next((c for c in self.stock["Categories"] if c["category"] == category), None)["products"]
        for p in c_products:
            products.append({"no.": counter,
                             "name": p["name"],
                             "rating": p["rating"],
                             "price": p["price"]})
            counter += 1

        product_table = Table(show_header=True, header_style="bold #03f4fc")
        product_table.add_column("No.", width=6)
        product_table.add_column("Product Name")
        product_table.add_column("Rating", justify="center")
        product_table.add_column("Price", justify="right")

        for product in products:
            product_table.add_row(f"{product['no.']}",
                                  product["name"],
                                  str(product["rating"]),
                                  f"₹{product['price']}")

        console.print(product_table)

        print("\nEnter item No. to edit it. Or enter 0 to return to previous menu.")
        option = input("\nWhich item would you like to edit? ").strip()
        if option == "0":
            return 0
        if option == "X":
            self.exit_market()
        for p in products:
            if option in (str(p["no."]), p["name"]):
                p_edit = next((product for product in c_products if product["name"] == p["name"]), None)
                return self.editing_process2(c_products, c_products.index(p_edit))
                # return self.editing_process(p_edit)
        else:
            self.flags["invalid_input"] = 1
            return 0

    def editing_process2(self, product_list, index):
        """
        Alternate function to implement editing that takes in a list and index to simulate pass by reference.
        :param product_list:
        :param index:
        :return:
        """
        self.clear()
        main_string = f"Editing Product: {product_list[index]['name']}"
        print(main_string)
        print("-" * (len(main_string) + 1))
        product_details = [
            ["1", "Name", product_list[index]["name"]],
            ["2", "Details", product_list[index]["details"]],
            ["3", "Rating", product_list[index]["rating"]],
            ["4", "Price(₹)", product_list[index]["price"]]
        ]
        self.current_product["name"] = product_list[index]["name"]
        print(tabulate(product_details, tablefmt="presto"))
        option = input("\nWhat would you like to edit? ")

        if option in product_details[0]:
            product_list[index]["name"] = input("Enter New Product Name: ").strip()
            self.current_product["changed_value"] = "Name"
        elif option in product_details[1]:
            product_list[index]["details"] = input("Enter New Product Details: ").strip()
            self.current_product["changed_value"] = "Details"
        elif option in product_details[2]:
            while True:
                try:
                    p_rating = float(input("Enter New Product Rating: ").strip())
                    if p_rating <= 0:
                        print("Invalid Value. Please try again.")
                        continue

                    product_list[index]["rating"] = p_rating
                    break
                except ValueError:
                    print("Invalid Value. Please try again.")
        elif option in product_details[3]:
            while True:
                try:
                    p_price = float(input("Enter New Product Price: ").strip())
                    if p_price <= 0:
                        print("Invalid Value. Please try again.")
                        continue
                    product_list[index]["price"] = p_price
                    self.current_product["changed_value"] = "Price"
                    break
                except ValueError:
                    print("Invalid Value. Please try again.")
        else:
            self.flags["invalid_input"] = 1
            return 0
        self.update_stock()
        return 1

    def remove_from_category(self):
        while True:
            self.clear()
            print("Remove from Category")
            print("-" * (len("Remove from Category") + 1))
            print(tabulate(self.categories, tablefmt="presto"))
            print("\nEnter 0 to return to previous menu.")
            option = input("Enter product category to remove item: ")
            if option == "0":
                return 0
            if option == "X":
                self.exit_market()
            for c in self.categories:
                if option in c:
                    return self.remove_item(c[1])
            else:
                self.flags["invalid_input"] = 1

    def remove_item(self, category):
        while True:
            self.clear()
            main_string = f"Browsing Category: {category}"
            print(main_string)
            print("-" * (len(main_string) + 1))
            products = []
            counter = 1
            for c in self.stock["Categories"]:
                if c["category"] == category:
                    for p in c["products"]:
                        products.append([str(counter), p["name"]])
                        counter += 1

            print(tabulate(products, tablefmt="presto"))
            print("\nEnter 0 to return to previous menu.")
            option = input("Enter product to remove item: ").strip().lower()
            if option == "0":
                return 0
            if option == "x":
                self.exit_market()
            for p in products:
                if option in p:
                    for c in self.stock["Categories"]:
                        if c["category"] == category:
                            for product in c["products"]:
                                if product["name"] == p[1]:
                                    self.current_product = product
                                    c["products"].remove(product)
                    self.flags["empty_category"] = self.check_empty_categories()
                    self.update_stock()
                    return 1
            else:
                self.flags["invalid_input"] = 1

    def check_empty_categories(self):
        for c in self.stock["Categories"]:
            if not c["products"]:
                self.empty_category = c["category"]
                self.stock["Categories"].remove(c)
                return 1
        else:
            return 0

    def main_menu(self):
        while True:
            self.clear()
            print("Main Menu")
            print("-" * (len("Main Menu") + 1))
            actions = [["1", "Browse Categories"], ["2", "View Cart"], ["3", "Exit"]]
            print(tabulate(actions, tablefmt="presto"))
            option = input("\nWhat would you like to do? ").strip()
            if option in actions[0]:
                self.browse_categories()
            elif option in actions[1]:
                self.view_cart()
            elif option in actions[2]:
                self.exit_market()
            else:
                self.flags["invalid_input"] = 1

    def browse_categories(self):
        while True:
            self.clear()
            print("Categories")
            print("-" * (len("Categories") + 1))
            print(tabulate(self.categories, tablefmt="presto"))
            print("\nEnter 0 to return to previous menu.")
            option = input("\nWhat would you like to do? ").strip()
            if option == "0":
                return 0
            if option == "X":
                self.exit_market()
            for c in self.categories:
                if option in c:
                    if self.browse_products(c[1]):
                        return 1
                    break
            else:
                self.flags["invalid_input"] = 1

    def browse_products(self, category):
        while True:
            self.clear()
            main_string = f"Browsing Category: {category}"
            print(main_string)
            print("-" * (len(main_string) + 1))
            products = []
            counter = 1
            for c in self.stock["Categories"]:
                if c["category"] == category:
                    for p in c["products"]:
                        products.append({"no.": counter,
                                         "name": p["name"],
                                         "rating": p["rating"],
                                         "price": p["price"]})
                        counter += 1

            product_table = Table(show_header=True, header_style="bold #03f4fc")
            product_table.add_column("No.", width=6)
            product_table.add_column("Product Name")
            product_table.add_column("Rating", justify="center")
            product_table.add_column("Price", justify="right")

            for product in products:
                product_table.add_row(f"{product['no.']}",
                                      product["name"],
                                      str(product["rating"]),
                                      f"₹{product['price']}")

            console.print(product_table)

            print("\nEnter item No. to add it to you cart.")
            print("Enter 0 to return to previous menu.")
            option = input("\nWhat would you like to do? ").strip()
            if option == "0":
                return 0
            if option == "X":
                self.exit_market()
            for p in products:
                if option in (str(p["no."]), p["name"]):
                    rprint(f"\n[cyan]{p['name']}[/cyan] has been selected.")
                    try:
                        qty = int(input("How many would you like to purchase? "))
                        if qty == 0:
                            return 0
                    except ValueError:
                        print("Sorry! We could not understand your input. 1 item has been added to your cart.")
                        qty = 1
                        time.sleep(5)
                    return self.add_to_cart(p, qty)
            else:
                self.flags["invalid_input"] = 1

    def add_to_cart(self, product, quantity=1):
        for c in self.cart:
            if c["name"] == product["name"]:
                c["quantity"] += quantity
                c["total"] = c["price"] * c["quantity"]
                self.current_product = {"name": c["name"], "quantity": quantity}
                self.flags["added_to_cart"] = 1
                break
        else:
            self.cart.append({"no.": (len(self.cart) + 1),
                              "name": product["name"],
                              "price": product["price"],
                              "quantity": quantity,
                              "total": (product["price"] * quantity)})
            self.current_product = self.cart[-1]
            self.flags["added_to_cart"] = 1
        self.update_cart_in_file()
        return 1

    def view_cart(self):
        while True:
            self.clear()
            if not self.cart:
                self.flags["cart_empty"] = 1
                return

            self.show_cart_table()
            print("Cart Actions")
            print("-" * (len("Cart Actions") + 1))
            actions = [["1", "Checkout"], ["2", "Remove Items"], ["3", "Clear Cart"]]

            print(tabulate(actions, tablefmt="presto"))
            print("\nEnter 0 to return to previous menu.")
            option = input("\nWhat would you like to do? ").strip()

            match option:
                case "0":
                    return 0
                case "X":
                    self.exit_market()
                case "1":
                    self.checkout()
                case "2":
                    self.flags["removed_from_cart"] = 1 if self.remove_from_cart() else 0
                    self.update_cart_in_file()
                case "3":
                    self.flags["cart_cleared"] = self.clear_cart()
                    return
                case _:
                    self.flags["invalid_input"] = 1

    def show_cart_table(self):
        table = Table(show_header=True, header_style="bold #03f4fc")
        table.add_column("No.", width=6)
        table.add_column("Product Name")
        table.add_column("Price", justify="right")
        table.add_column("Quantity", justify="center")
        table.add_column("Total", justify="right")

        grand_total = 0

        for c in self.cart:
            if c == self.cart[-1]:
                table.add_row(str(c["no."]), c["name"], f"₹{c['price']}", str(c["quantity"]),
                              f"₹{c['total']}", end_section=True)
            else:
                table.add_row(str(c["no."]), c["name"], f"₹{c['price']}", str(c["quantity"]),
                              f"₹{c['total']}")
            grand_total += c["total"]
        table.add_row("", "", "", "Grand Total", f"₹{grand_total}")

        console.print(table)

    def remove_from_cart(self):
        self.clear()
        self.show_cart_table()
        print("\nEnter 0 to return to previous menu.")
        option = input("\nEnter the No. of the item you want to remove: ").strip()

        if option == "0":
            return 0
        elif option == "X":
            self.exit_market()
        for c in self.cart:
            if option == str(c["no."]):
                if c["quantity"] == 1:
                    self.current_product = c.copy()
                    self.cart.remove(c)
                    self.update_cart()
                    return 1
                else:
                    rprint(f"\nThe quantity of the item in cart is [b][u]{c['quantity']}[/u][/b].")
                    print("Enter the number of items you want to remove or type 'Y' to remove all.", end="")
                    reduce = input(" ").strip().lower()
                    if reduce == "y":
                        self.current_product = c.copy()
                        self.cart.remove(c)
                        self.update_cart()
                        return 1
                    try:
                        if int(reduce) >= c["quantity"]:
                            self.current_product = c.copy()
                            self.cart.remove(c)
                            self.update_cart()
                            return 1
                        else:
                            c["quantity"] = c["quantity"] - int(reduce)
                            self.update_cart()
                            self.current_product = c.copy()
                            self.current_product["quantity"] = reduce
                            return 1
                    except ValueError:
                        self.flags["invalid_input"] = 1
                        return 0

    def update_cart(self):
        counter = 1
        for item in self.cart:
            item["no."] = counter
            counter += 1
            item["total"] = item["price"] * item["quantity"]

    def exit_market(self):
        if self.cart:
            self.clear()
            print("\nYour cart has items in it.")
            answer = input("Do you still wish to exit?(Y/N) ").strip().lower()
            if answer != "y":
                self.main_menu()
        print("\nThank you for shopping with Demo Marketplace.\n")
        sys.exit()

    def clear(self):
        os.system("cls")
        print(pyfiglet.figlet_format("market"))
        self.show_message()
        self.show_cart_at_top()

    def show_message(self):
        """
        Method that checks for flags. If a flag is set to 1, it prints the corresponding message and then resets it.
        :return: None
        """
        if self.flags["invalid_input"] == 1:
            rprint("[red on white i]Sorry! We could not understand your response. Please try again.[/red on white i]")
            self.flags["invalid_input"] = 0
        if self.flags["added_to_cart"] == 1:
            if self.current_product:
                rprint(f"[cyan]{self.current_product['quantity']}[/cyan] "
                       f"[green]{self.current_product['name']}(s)[/green] added to cart.")
                self.flags["added_to_cart"] = 0
                self.current_product = {}
        if self.flags["first_entry"] == 1:
            rprint(f"Hello, [b cyan]{self.user['username']}[/b cyan]! Welcome to [u]Demo Marketplace[/u]")
            self.flags["first_entry"] = 0
        if self.flags["cart_cleared"] == 1:
            rprint("[red on white]Your cart has been cleared.[/red on white]")
            self.flags["cart_cleared"] = 0
        if self.flags["cart_empty"] == 1:
            rprint("Your cart is empty. Select [b u]Browse Categories[/b u] and add some items to it.")
            self.flags["cart_empty"] = 0
        if self.flags["removed_from_cart"] == 1:
            rprint(f"[red]{self.current_product['quantity']} {self.current_product['name']}(s)[/red]"
                   f" removed from cart.")
            self.flags["removed_from_cart"] = 0
            self.current_product = {}
        if self.flags["item_removed"] == 1:
            rprint(f"[red]{self.current_product['name']}[/red] removed from inventory.")
            self.flags["item_removed"] = 0
            self.current_product = {}
        if self.flags["item_added"] == 1:
            rprint(f"[white on green]{self.current_product['name']}[/white on green] added to inventory.")
            self.flags["item_added"] = 0
            self.current_product = {}
        if self.flags["item_edited"] == 1:
            rprint(f"[cyan]{self.current_product['changed_value']}[/cyan] of "
                   f"[green]{self.current_product['name']}[/green] has been edited.")
            self.flags["item_edited"] = 0
            self.current_product = {}
        if self.flags["empty_category"] == 1:
            rprint(f"[r][white on red]{self.empty_category}[/white on red] category is empty and has been removed.[/r]")
            self.flags["empty_category"] = 0
            self.empty_category = ""
        print("")

    def show_cart_at_top(self):
        if self.cart:
            rprint(f"You have {len(self.cart)} items in your cart. | "
                   f"Cart Value: ₹{sum([c["total"] for c in self.cart])}\n")

    def checkout(self):
        while True:
            self.clear()
            self.show_cart_table()
            actions = [["1", "UPI"], ["2", "Credit/Debit Card"], ["3", "Online Banking"]]

            print("Checkout")
            print("-" * (len("Checkout") + 1))

            print(tabulate(actions, tablefmt="presto"))
            print("\nPlease select a Payment method.")
            print("\nEnter 0 to return to previous menu.")
            option = input("\nWhat would you like to do? ").strip()
            try:
                if option == "0":
                    return 0
                elif option == "X":
                    self.exit_market()
                elif int(option) in [1, 2, 3]:
                    self.clear_cart(1)
                    self.exit_market()
                else:
                    self.flags["invalid_input"] = 1
            except ValueError:
                self.flags["invalid_input"] = 1

    def clear_cart(self, force: bool = 0):
        """
        Clears the cart with a warning message. Does not give warning if the 'force' variable is set to True.
        :type force: Boolean
        """
        if force == 0:
            answer = input("\nAre you sure you wish to clear the cart? (Y/N) ").strip().lower()
            if answer == "y":
                self.cart = []
                self.update_cart_in_file()
                return 1
        else:
            self.cart = []
            self.update_cart_in_file()
            return


# Define Main Function
def main():
    Market()


# Main Function
if __name__ == '__main__':
    main()

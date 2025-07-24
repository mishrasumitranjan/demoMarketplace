from rich.console import Console
from rich.table import Table
from rich import box


# Define Main Function
def main():
    console = Console()

    cart_table = [
        {"name": "Alpha", "quantity": 2, "price": 299},
        {"name": "Beta", "quantity": 1, "price": 59},
        {"name": "Gamma", "quantity": 5, "price": 130},
        {"name": "Eta", "quantity": 6, "price": 50}
    ]

    counter = 1

    table = Table(show_header=True, header_style="bold #03f4fc")
    table.add_column("No.", width=6)
    table.add_column("Product Name")
    table.add_column("Price", justify="right")
    table.add_column("Quantity", justify="center")
    table.add_column("Total", justify="right")

    grand_total = 0

    for c in cart_table:
        c["no."] = counter
        c["total"] = c["quantity"] * c["price"]
        counter += 1
        if c == cart_table[-1]:
            table.add_row(str(c["no."]), c["name"], f"₹{c['price']}", str(c["quantity"]),
                          f"₹{c['total']}", end_section=True)
        else:
            table.add_row(str(c["no."]), c["name"], f"₹{c['price']}", str(c["quantity"]),
                          f"₹{c['total']}")
        grand_total += c["total"]
    table.add_row("", "", "", "Grand Total", f"₹{grand_total}")

    console.print(table)


# Define Additional Functions


# Main Function
if __name__ == '__main__':
    main()

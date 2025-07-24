from rich.tree import Tree
from rich import print as rprint
from rich.console import Console
from rich.rule import Rule


# Define Main Function
def main():

    console = Console()

    tree = Tree("Alpha")
    node = tree.add("Beta")
    node.add("Theta")
    node.add("Eta")
    tree.add("Gamma").add("Sigma")

    rprint(tree)

    rprint(Rule(style="white"))

    a = 5
    console.print(f"I saw {a} horses that [u]should[/u] not [b]have[/b] been [r]allowed[/r] into the arena.")
    rprint(f"I saw {a} horses that [u]should[/u] not [b cyan]have[/b cyan]"
           f"been [i red on white]allowed[/i red on white] into the [dark green]arena[/dark green].")


# Define Additional Functions


# Main Function
if __name__ == '__main__':
    main()

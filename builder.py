import sys

try:
	import typer
	from rich import print
except ImportError:
	print('Python 3.11 required with packages: typer[all]')
	sys.exit(-1)

app = typer.Typer(add_completion=False)


@app.command()
def make(images: list[str] = typer.Option(tuple(), '-i', '--image', show_default=False, help='Base images to create ssh server from.')):
	"""
	Generate necessary files for building.

	builder --image alpine --image python:3.11-alpine
	"""
	if not len(images):
		print(r'[red]No base images specified. Use --image option, see --help for more information.[/]')
		raise typer.Exit(-2)


if __name__ == '__main__':
	app()

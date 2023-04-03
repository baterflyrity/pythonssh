import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
	import typer
	from rich import print
except ImportError:
	print('Python 3.11 required with packages: typer[all]')
	sys.exit(-1)

app = typer.Typer(add_completion=False)


def _fill_template_variable(template: str, name: str, value: str) -> str:
	return re.sub(r'({{\s*' + name + r'\s*}})', value, template, re.IGNORECASE | re.MULTILINE)


def _fill_template(template: str, variables: dict[str, str]) -> str:
	text = template
	for name, value in variables.items():
		text = _fill_template_variable(text, name, value)
	return text


def _autotag(image: str) -> str:
	if image.startswith('python:'):
		return image.split(':')[-1].split('-')[0].strip()
	return image.strip()


def _find_tag(dockerfile: str) -> str | None:
	for line in dockerfile.split('\n'):
		if line.startswith('# TAG='):
			return line.removeprefix('# TAG=').strip()


@app.command(no_args_is_help=True)
def make(images: list[str] = typer.Option(tuple(), '-i', '--image', show_default=False, help='Base images to create ssh server from.'), password: str = typer.Option('123', '-p', '--password', help='Root user password.'), autotag: bool = True):
	"""
	Generate necessary files for building.

	builder --image alpine --image python:3.11-alpine
	"""
	if not len(images):
		print(r'[red]No base images specified. Use --image option, see --help for more information.[/]')
		raise typer.Exit(-2)
	template_dockerfile = (Path.cwd() / 'Dockerfile').read_text('utf8')
	template_entry = (Path.cwd() / 'entry.sh').read_text('utf8')
	template_setpasswd = (Path.cwd() / 'setpasswd.sh').read_text('utf8')
	dist_root = Path.cwd() / 'dockerfiles'
	if dist_root.exists():
		shutil.rmtree(dist_root)
	dist_root.mkdir(exist_ok=True, parents=True)
	for image in images:
		variables = {
			'password':   password.strip(),
			'base-image': image.strip(),
			'tag':        _autotag(image) if autotag else image.strip().replace(':', '_')
		}
		(dist_root / (image.replace('\\', '_').replace('/', '_').replace(':', '_') + '.dockerfile')).write_text(_fill_template(template_dockerfile, variables), 'utf8', newline='\n')
		(dist_root / 'entry.sh').write_text(_fill_template(template_entry, variables), 'utf8', newline='\n')
		(dist_root / 'setpasswd.sh').write_text(_fill_template(template_setpasswd, variables), 'utf8', newline='\n')


@app.command()
def build(name: str = 'pythonssh'):
	"""
	Build docker images from generated dockerfiles.
	"""
	dist_root = Path.cwd() / 'dockerfiles'
	for f in dist_root.glob('*.dockerfile'):
		if f.is_file():
			print(f'Building {f}...')
			tag = _find_tag(f.read_text('utf8'))
			if not tag:
				print(f'[red]Can not find tag for image {f}.[/]')
				raise typer.Exit(-3)
			try:
				print(subprocess.check_output(f'docker build -t "{name}:{tag}" -f "{f}" "{dist_root}"').decode('utf8'))
			except subprocess.CalledProcessError as e:
				print(f'[red]Can not build image {f}: {e}[/]')
				raise typer.Exit(-4)
			print(f'Built {f}.')


@app.command()
def push(name: str = 'pythonssh'):
	"""
	Push all built images.
	"""
	dist_root = Path.cwd() / 'dockerfiles'
	for f in dist_root.glob('*.dockerfile'):
		if f.is_file():
			tag = _find_tag(f.read_text('utf8'))
			if not tag:
				print(f'[red]Can not find tag for image {f}.[/]')
				raise typer.Exit(-3)
			print(f'Pushing {name}:{tag}...')
			try:
				print(subprocess.check_output(f'docker push "{name}:{tag}"').decode('utf8'))
			except subprocess.CalledProcessError as e:
				print(f'[red]Can not push image {f}: {e}[/]')
				raise typer.Exit(-5)


if __name__ == '__main__':
	app()

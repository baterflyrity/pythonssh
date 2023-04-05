import re
import shutil
import subprocess
from pathlib import Path

import typer
from rich import print

app = typer.Typer(add_completion=False)
template_root = Path.cwd() / 'template'
build_root = Path.cwd() / 'build'


def _fill_template_variable(template: str, name: str, value: str) -> str:
	return re.sub(r'({{\s*' + str(name) + r'\s*}})', str(value), str(template), re.IGNORECASE | re.MULTILINE)


def _fill_template(path: Path, template: str, variables: dict[str, str]) -> tuple[Path, str]:
	path_text = str(path)
	text = template
	for name, value in variables.items():
		path_text = _fill_template_variable(path_text, name, value)
		text = _fill_template_variable(text, name, value)
	return Path(path_text), text


def _autotag(image: str) -> str:
	chunks = image.strip().split(':')
	if len(chunks) == 1:
		version = flavor = None
	else:
		chunks2 = chunks[1].split('-')
		version = chunks2[0]
		if len(chunks2) == 1:
			flavor = None
		else:
			flavor = '-'.join(chunks2[1:])
	chunks3 = chunks[0].split('/')
	name = chunks3[-1]
	if len(chunks3) == 1:
		user = None
	else:
		user = chunks3[0]

	return version or name


def _find_tag(dockerfile: str) -> str | None:
	for line in dockerfile.split('\n'):
		if line.startswith('# TAG='):
			return line.removeprefix('# TAG=').strip()


def _prepare_build_root(root: Path) -> None:
	if root.exists():
		shutil.rmtree(root)
	root.mkdir(exist_ok=True, parents=True)


@app.command(no_args_is_help=True)
def make(images: list[str] = typer.Option(tuple(), '-i', '--image', show_default=False, help='Base images to create ssh server from. Can repeat.'), password: str = typer.Option('123', '--password', '-p', help='Root user password to login via ssh.'), autotag: bool = True):
	"""
	Generate necessary files for building.

	builder --image alpine --image python:3.11-alpine
	"""
	if not len(images):
		print(r'[red]No base images specified. Use --image option, see --help for more information.[/]')
		raise typer.Exit(-1)
	_prepare_build_root(build_root)
	templates = [(f.relative_to(template_root), f.read_text('utf8')) for f in template_root.rglob('*') if f.is_file()]
	for i, image in enumerate(images):
		variables = {
			'image':      image,
			'image-safe': image.replace('\\', '_').replace('/', '_').replace(':', '_'),
			'base-image': image.strip(),
			'tag':        _autotag(image) if autotag else image.strip().replace(':', '_'),
			'index':      i,
			'password':   password,
		}
		for template, text in templates:
			path, content = _fill_template(template, text, variables)
			path = build_root / path
			path.parent.mkdir(exist_ok=True, parents=True)
			path.write_text(content, 'utf8', newline='\n')


@app.command()
def build(name: str = typer.Option('pythonssh', '--name', '-n', help='Image name.'), user: str = typer.Option('', '--user', '-u', help='Image name user prefix, e.g. user/name. If not specified only name is used.', show_default=False), latest: str = typer.Option('', '--latest', '-l', help='Tag to mark as latest image if such exists.')):
	"""
	Build docker images from generated dockerfiles.
	"""
	if user:
		name = f'{user}/{name}'
	images = []
	for f in build_root.glob('*.dockerfile'):
		if f.is_file():
			print(f'Building {f}...')
			tag = _find_tag(f.read_text('utf8'))
			if not tag:
				print(f'[red]Can not find tag for image {f}.[/]')
				raise typer.Exit(-2)
			image = f'{name}:{tag}'
			try:
				print(subprocess.check_output(f'docker build -t "{image}" -f "{f}" "{build_root}"').decode('utf8'))
			except subprocess.CalledProcessError as e:
				print(f'[red]Can not build image {f}: {e}[/]')
				raise typer.Exit(-3)
			else:
				images.append(image)
				print(f'Built {f}.')
			if latest == tag:
				try:
					print(subprocess.check_output(f'docker tag "{image}" "{name}:latest"').decode('utf8'))
				except subprocess.CalledProcessError as e:
					print(f'[red]Can not tag image {f} as latest: {e}[/]')
					raise typer.Exit(-4)
				else:
					images.append(f'{name}:latest')
					print(f'Tagged {f} as latest.')
	(build_root / 'images.list').write_text('\n'.join([str(image) for image in images]), encoding='utf8', newline='\n')


@app.command()
def push():
	"""
	Push all built images.
	"""
	images = [l for l in [line.strip() for line in (build_root / 'images.list').read_text('utf8').split('\n')] if l]
	for image in images:
		print(f'Pushing {image}...')
		try:
			print(subprocess.check_output(f'docker push "{image}"').decode('utf8'))
		except subprocess.CalledProcessError as e:
			print(f'[red]Can not push image {image}: {e}[/]')
			raise typer.Exit(-5)


if __name__ == '__main__':
	app()

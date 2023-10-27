import click
import tftpy

@click.group()
def cli():
    pass

@cli.command()
@click.option('--host', default='localhost', help='TFTP server host.')
@click.option('--port', default=69, help='TFTP server port.')
@click.argument('remote_filename')
@click.argument('local_filename')
def download(host, port, remote_filename, local_filename):
    """Download a file from the TFTP server."""
    client = tftpy.TftpClient(host, port)
    client.download(remote_filename, local_filename)
    click.echo(f"Downloaded {remote_filename} to {local_filename}")


if __name__ == '__main__':
    cli()
# python tftp_client.py download --host localhost --port 69 remote_file.txt local_file.txt
# python client1.py download --host localhost --port 69 test.txt local_file.txt

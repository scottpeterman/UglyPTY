import click
import logging
import tftpy


@click.command()
@click.option('--path', default='./files', help='The root directory to serve files from.')
@click.option('--port', default=69, help='The port to listen on.')
def start_tftp_server(path, port):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("tftpy.TftpServer")

    try:
        server = tftpy.TftpServer(path)
        server.listen('0.0.0.0', port)

    except Exception as e:
        logger.exception(f"Failed to start the server: {e}")


if __name__ == '__main__':
    start_tftp_server()

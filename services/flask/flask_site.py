import logging
from website import create_app

app = create_app()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/hello')
def hello():
    app.logger.debug('this is DEBUG')
    app.logger.info('this is INFO')
    app.logger.warning('WARNING')
    app.logger.error('ERROR')
    app.logger.critical('CRITICAL')
    return "<h1 style='color:blue'>Hello There!</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


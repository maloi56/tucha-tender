import locale
import requests

from flask import Flask, redirect, url_for
from app import config
from app.extentions import login_manager, migrate, bootstrap
from app.model import db
from app.tender_role.parser import scheduler, start_scheduler
from app.auth.login import auth
from app.director_role.director import director
from app.hr_role.hr import hr
from app.instruments_role.instruments import instruments
from app.materials_role.materials import materials
from app.tender_role.tender import tender
from app.tender_role.parser import scheduler, start_scheduler


def create_app(config=config.base_config):
    """Returns an initialized Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)
    register_filters(app)
    login_manager.init_app(app)
    register_blueprints(app)
    register_extensions(app)
    register_errorhandlers(app)
    start_scheduler()
    return app


def register_extensions(app):
    """Register extensions with the Flask application."""
    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    """Register blueprints with the Flask application."""
    app.register_blueprint(director, url_prefix='/director')
    app.register_blueprint(hr, url_prefix='/hr')
    app.register_blueprint(instruments, url_prefix='/instruments')
    app.register_blueprint(materials, url_prefix='/materials')
    app.register_blueprint(tender, url_prefix='/tender')
    app.register_blueprint(auth, url_prefix='/auth')


def float_to_currency(value):
    locale.setlocale(locale.LC_ALL, '')  # Устанавливаем локаль по умолчанию
    return locale.currency(value, grouping=True, symbol=True)


def register_filters(app):
    app.jinja_env.filters['float_to_currency'] = float_to_currency


def register_errorhandlers(app):
    """Register error handlers with the Flask application."""

    def render_error(e):
        return redirect(url_for('auth.login'))

    for e in [
        requests.codes.INTERNAL_SERVER_ERROR,
        requests.codes.NOT_FOUND,
        requests.codes.UNAUTHORIZED,
    ]:
        app.errorhandler(e)(render_error)
from flask import render_template, current_app
from app import db
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    current_app.logger.warning(f'404 error: {error}')
    return render_template('errors/404.html', title='Page Not Found'), 404

@bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    current_app.logger.warning(f'403 error: {error}')
    return render_template('errors/403.html', title='Access Forbidden'), 403

@bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    current_app.logger.error(f'Server error: {error}')
    db.session.rollback()
    return render_template('errors/500.html', title='Server Error'), 500

@bp.app_errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    current_app.logger.warning(f'413 error: {error}')
    return render_template('errors/413.html', title='File Too Large'), 413
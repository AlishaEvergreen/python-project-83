import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from page_analyzer.repository import UrlChecksRepository, UrlsRepository
from page_analyzer.utils import normalize_url, parse_html_metadata, validate

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

DATABASE_URL = app.config["DATABASE_URL"]
URLS_REPO = UrlsRepository(DATABASE_URL)
CHECKS_REPO = UrlChecksRepository(DATABASE_URL)


@app.errorhandler(404)
def not_found(error):
    """Renders a 404 error page."""
    return render_template('404.html'), 404


@app.route("/")
def home():
    """Renders the home page with a form for adding URLs."""
    error = session.pop('error', None)
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'index.html',
        url={},
        error=error,
        messages=messages
    )


@app.route('/urls/<int:id>')
def show_url(id):
    """Renders a page with details for a specific URL."""
    url_data = URLS_REPO.get_url_data_by_id(id)

    if not url_data:
        abort(404)

    checks_data = CHECKS_REPO.get_checks_by_id(id)
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'layout_url.html',
        url=url_data,
        checks=checks_data,
        messages=messages
    )


@app.route('/urls')
def show_urls():
    """Render a page with a list of all URLs and their latest checks."""
    urls = CHECKS_REPO.get_urls_with_last_check()
    messages = get_flashed_messages(with_categories=True)

    return render_template('layout_urls.html', urls=urls, messages=messages)


@app.post('/urls')
def create_url():
    """Handles URL submission and validation."""
    url_data = request.form.get('url', '').strip()
    error = validate(url_data)
    normalized_url = normalize_url(url_data)

    if error:
        session['error'] = error
        return render_template('index.html', url=url_data, error=error), 422

    existing_url = URLS_REPO.get_url_data_by_name(normalized_url)
    if existing_url:
        flash("Страница уже существует", "info")
        return redirect(url_for('show_url', id=existing_url['id']))

    url_id = URLS_REPO.save_url({'url': normalized_url})
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))


@app.post('/urls/<int:id>/checks')
def check_url(id):
    """Performs a check on a URL and saves the results."""
    url = URLS_REPO.get_url_data_by_id(id)

    try:
        response = requests.get(url['name'], timeout=10)
        response.raise_for_status()

        h1, title, description = parse_html_metadata(response.text)

        CHECKS_REPO.save_url_check(
            id,
            response.status_code,
            h1,
            title,
            description
        )
        flash("Страница успешно проверена", "success")
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")

    return redirect(url_for('show_url', id=id))

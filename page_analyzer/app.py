import os
import requests

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.repository import UrlChecksRepository, UrlsRepository
from page_analyzer.utils import normalize_url, validate

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

urls_repo = UrlsRepository()
checks_repo = UrlChecksRepository()


@app.route("/")
def home():
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'index.html',
        url={},
        messages=messages
    )


@app.route('/urls/<int:id>')
def show_url(id):
    url_data = urls_repo.get_url_data_by_id(id)
    checks_data = checks_repo.get_checks_by_id(id)

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'url.html',
        url=url_data,
        checks=checks_data,
        messages=messages)


@app.route('/urls')
def show_urls():
    urls = checks_repo.get_urls_with_last_check()
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'urls.html',
        urls=urls,
        messages=messages
        )


@app.route('/urls', methods=['POST'])
def create_url():
    url_data = request.form.get('url', '').strip()

    error = validate(url_data)
    normalized_url = normalize_url(url_data)

    if error:
        flash(error, 'danger')
        return redirect(url_for('home'))

    existing_url = urls_repo.get_url_data_by_name(normalized_url)
    if existing_url:
        flash("Страница уже существует", "info")
        return redirect(url_for('show_url', id=existing_url['id']))

    url_id = urls_repo.save_url({'url': normalized_url})
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    url = urls_repo.get_url_data_by_id(id)

    try:
        response = requests.get(url['name'], timeout=10)
        response.raise_for_status()
        status_code = response.status_code
        checks_repo.save_url_check(id, status_code)
        flash("Страница успешно проверена", "success")
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")

    return redirect(url_for('show_url', id=id))

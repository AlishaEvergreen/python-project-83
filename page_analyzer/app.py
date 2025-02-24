import os

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
    urls_repo = UrlsRepository()
    url_data = urls_repo.get_url_data_by_id(id)

    checks_repo = UrlChecksRepository()
    checks_data = checks_repo.get_checks_by_id(id)

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'url.html',
        url=url_data,
        checks=checks_data,
        messages=messages)


@app.route('/urls')
def show_urls():
    repo = UrlsRepository()
    urls = repo.get_entities()
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

    repo = UrlsRepository()

    if error:
        flash(error, 'danger')
        return redirect(url_for('home'))

    existing_url = repo.get_url_data_by_name(normalized_url)
    if existing_url:
        flash("Страница уже существует", "info")
        return redirect(url_for('show_url', id=existing_url['id']))

    url_id = repo.save_url({'url': normalized_url})
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    repo = UrlChecksRepository()
    repo.save_url_check({'id': id})
    return redirect(url_for('show_url', id=id))

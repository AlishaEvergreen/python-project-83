import os

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    get_flashed_messages
)
from page_analyzer.repository import get_db, UrlsRepository
from page_analyzer.utils import normalize_url, validate


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")


repo = UrlsRepository(get_db(app))


@app.route("/")
def home():
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'index.html',
        url={'id': '', 'name': '', 'created_at': ''},
        messages=messages
    )


@app.route('/urls', methods=['POST'])
def check_url():
    url_data = request.form.get('url', '').strip()

    error = validate(url_data)
    normalized_url = normalize_url(url_data)

    if error:
        flash(error, 'error')
        return redirect(url_for('home'))

    if repo.get_url_by_name(normalized_url):
        flash("Страница уже существует", "warning")
        return redirect(url_for('home'))

    repo.save({'url': normalized_url})
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('home'))

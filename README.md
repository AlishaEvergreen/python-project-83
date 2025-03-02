### Hexlet tests and linter status:
[![Actions Status](https://github.com/AlishaEvergreen/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/AlishaEvergreen/python-project-83/actions)
[![Python CI](https://github.com/AlishaEvergreen/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/AlishaEvergreen/python-project-83/actions/workflows/pyci.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/55d96be536cab6c6262b/maintainability)](https://codeclimate.com/github/AlishaEvergreen/python-project-83/maintainability)

### Production Build:
[![Live Demo](https://img.shields.io/badge/Live_Demo-Available-blue)](https://python-project-83-kqoq.onrender.com)

## Page Analyzer

**Page Analyzer** is a website that analyzes specified pages for SEO suitability, similar to [PageSpeed Insights](https://pagespeed.web.dev/).  
It's a Flask-based web application demonstrating core web development principles, including MVC architecture, routing, database interaction, and automated deployment using render.com.

## Requirements
```
- Python 3.11+
- PostgreSQL database (to store analyzed data)
- Make (for running commands)
```

## Installation

### 📂 Clone the Repository:
```
git clone https://github.com/AlishaEvergreen/python-project-83.git page-analyzer
```

### 🚀 Install Dependencies and Set Up the Project: 
```
make build
```
### ⚙️ Start the Development Server: 
```
make dev
```
### 🌐 Start the Production Server: 
```
make start
```

## Additional Setup

### After cloning the repository, navigate to the project folder using the following command:
```
cd page-analyzer
```
### If you don’t have Git installed, you can download the project as a ZIP archive:
- Go to the repository page: [python-project-83](https://github.com/AlishaEvergreen/python-project-83).
- Click the Code button (green button on the right).
- Select Download ZIP.
- Extract the archive and navigate to the project folder.

### Create a Database
- Ensure PostgreSQL is installed on your system.
- Create a new database: ```createdb database_name```
- Configure the database connection in the .env file (see below).

### Add .env File
- Create a .env file in the root folder of the project.
- Add the following variables to it:
```
DATABASE_URL=postgresql://username:password@localhost:5432/page_analyzer
SECRET_KEY=your_secret_key_here
```
Replace username, password, and your_secret_key_here with your own values.

## ❤️ Acknowledgements
### Thanks for stopping by, buddy! If you find this tool helpful, don't forget to give it a ⭐ on GitHub!
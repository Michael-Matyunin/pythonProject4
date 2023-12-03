import mysql.connector
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Zxdf20032013",
    database="online_cinema"
)

app = Flask(__name__, template_folder='templates')
app.secret_key = '3794374927492734092749274'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']

        mycursor = mydb.cursor()
        insert_query = "INSERT INTO user (Login, Password, Email, rating, Number_Credit_Card, ID_Subscription) VALUES (%s, %s, %s, 'User', 1111, 1)"
        user_data = (login, password, email)
        mycursor.execute(insert_query, user_data)

        mydb.commit()
        mycursor.close()

        session['user'] = login  # Автоматически входим пользователя в систему

        # После успешной регистрации перенаправляем на личный кабинет
        return redirect(url_for('show_user_profile', username=login))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['loginUsername']
        password = request.form['loginPassword']

        try:
            mycursor = mydb.cursor()
            query = "SELECT * FROM user WHERE Login = %s AND Password = %s"
            user_data = (login, password)
            mycursor.execute(query, user_data)
            user = mycursor.fetchone()  # Получаем данные пользователя из базы данных

            if user:
                session['user'] = login  # Добавляем пользователя в сессию

                # Обновляем время последнего входа в базе данных
                try:
                    update_query = "UPDATE user SET Last_Login = %s WHERE Login = %s"
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    user_data = (current_time, login)
                    mycursor.execute(update_query, user_data)
                    mydb.commit()
                    mycursor.close()

                    return render_template('login_success.html')
                except mysql.connector.Error as err:
                    print("Ошибка при обновлении времени последнего входа:", err)
                    return "Ошибка при входе."
            else:
                return "Login failed. Please check your credentials."

        except mysql.connector.Error as err:
            print("Ошибка при выполнении запроса к базе данных:", err)
            return "Произошла ошибка при попытке входа."
        finally:
            mycursor.close()

    return render_template('login.html')


import json


# Вместо возврата HTML вернем данные в формате JSON


@app.route('/sort_subscriptions', methods=['POST'])
def sort_subscriptions():
    sort_by = request.form.get('sort_by')

    subscriptions = get_subscriptions(sort_by)

    if subscriptions:
        return json.dumps(subscriptions)  # Возврат данных в формате JSON
    else:
        return json.dumps({"error": "Произошла ошибка при получении отсортированных подписок."})


def get_subscriptions(sort_by=None):
    try:
        cursor = mydb.cursor()
        query = "SELECT ID_Subscription, Subscription_title, Subscription_price, Subscription_duration FROM subscription"

        if sort_by == 'price':
            query += " ORDER BY CAST(SUBSTRING_INDEX(Subscription_price, ' ', 1) AS UNSIGNED)"
        elif sort_by == 'duration':
            query += " ORDER BY Subscription_duration"

        cursor.execute(query)
        subscriptions = cursor.fetchall()
        cursor.close()
        return subscriptions
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


# Отображение данных в user_profile
@app.route('/user_profile/<username>')
def show_user_profile(username):
    user_data = get_user_data(username)
    subscriptions = get_subscriptions()  # Получение подписок
    directors = get_directors()  # Получение списка режиссеров
    countries = get_countries()  # Получение списка стран
    countries_actors = filter_actors_by_country

    actors = get_actors_data()  # Получение данных об актерах

    if user_data:
        films = get_films()  # Получение фильмов
        return render_template('user_profile.html', user=user_data, subscriptions=subscriptions, films=films,
                               directors=directors, countries=countries, actors=actors, countries_actors=countries_actors)
    else:
        return "Пользователь не найден"



@app.route('/sort_films', methods=['POST'])
def sort_films():
    sort_by = request.form.get('sort_by')
    films = get_films(sort_by)

    if films:
        return jsonify(films)
    else:
        return jsonify({"error": "Произошла ошибка при получении отсортированных фильмов."})


def get_films(sort_by=None):
    try:
        cursor = mydb.cursor()
        query = "SELECT ID_Film, Title, Duration, Year_of_release, Country, Director FROM film"

        if sort_by == 'duration':
            query += " ORDER BY Duration"
        elif sort_by == 'year':
            query += " ORDER BY Year_of_release"

        cursor.execute(query)
        films = cursor.fetchall()
        cursor.close()

        # Преобразование данных в список словарей для удобства обработки в шаблоне
        films_list = []
        for film in films:
            film_dict = {
                'id': film[0],
                'title': film[1],
                'duration': film[2],
                'year': film[3],
                'country': film[4],
                'director': film[5]
            }
            films_list.append(film_dict)

        return films_list
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


def get_directors():
    try:
        cursor = mydb.cursor()
        query = "SELECT DISTINCT Director FROM film"
        cursor.execute(query)
        directors = cursor.fetchall()
        cursor.close()
        return [director[0] for director in directors] if directors else []
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return []


def get_countries():
    try:
        cursor = mydb.cursor()
        query = "SELECT DISTINCT Country FROM film"
        cursor.execute(query)
        countries = cursor.fetchall()
        cursor.close()
        return [country[0] for country in countries] if countries else []
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return []


def filter_films_by_director(director_name):
    try:
        cursor = mydb.cursor()
        query = "SELECT ID_Film, Title, Duration, Year_of_release, Country, Director FROM film WHERE Director = %s"
        cursor.execute(query, (director_name,))
        films = cursor.fetchall()
        cursor.close()
        if films:
            print(f"Найдено фильмов для режиссера '{director_name}': {len(films)}")
            return films
        else:
            print(f"Фильмы для режиссера '{director_name}' не найдены")
            return []
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


def filter_films_by_country(country_name):
    try:
        cursor = mydb.cursor()
        query = "SELECT ID_Film, Title, Duration, Year_of_release, Country, Director FROM film WHERE Country = %s"
        cursor.execute(query, (country_name,))
        films = cursor.fetchall()
        cursor.close()
        if films:
            print(f"Найдено фильмов для страны '{country_name}': {len(films)}")
            return films
        else:
            print(f"Фильмы для страны '{country_name}' не найдены")
            return []
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


films_director = filter_films_by_director('Louis Leterrier')
print(films_director)  # Печатает фильмы, найденные для режиссера 'Gore Verbinski'

# Проверка функции filter_films_by_country
films_country = filter_films_by_country('Japan')
print(films_country)


@app.route('/filter_films', methods=['POST'])
def filter_films():
    filter_type = request.form.get('filter_type')
    filter_value = request.form.get('filter_value')

    if filter_type == 'director':
        films = filter_films_by_director(filter_value)
    elif filter_type == 'country':
        films = filter_films_by_country(filter_value)
    else:
        films = []

    if films is not None:
        return jsonify(films)
    else:
        return jsonify({"error": "Произошла ошибка при фильтрации фильмов."})


@app.route('/actors')
def get_actors_data():
    try:
        cursor = mydb.cursor()
        query = "SELECT ID_Actor, Name, Last_Name, Place_birth, pupular_film FROM actor"
        cursor.execute(query)
        actors_data = cursor.fetchall()
        cursor.close()

        # Преобразование данных об актерах в список словарей
        actors_list = []
        for actor in actors_data:
            actor_dict = {
                'ID_Actor': actor[0],
                'Name': actor[1],
                'Last_Name': actor[2],
                'Place_birth': actor[3],
                'pupular_film': actor[4]
            }
            actors_list.append(actor_dict)

        return actors_list

    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return "Произошла ошибка при получении данных об актерах"


def filter_actors_by_country(country_name):
    try:
        if not country_name:
            print("Не указано название страны для фильтрации актеров")
            return []

        cursor = mydb.cursor()
        query = "SELECT ID_Actor, Name, Last_Name, Place_birth, pupular_film FROM actor WHERE Country = %s"
        cursor.execute(query, (country_name,))
        actors = cursor.fetchall()
        cursor.close()

        print(f"Получен запрос на фильтрацию актеров по стране '{country_name}'")
        if actors:
            print(f"Найдено актеров для страны '{country_name}': {len(actors)}")
            return actors
        else:
            print(f"Актеры для страны '{country_name}' не найдены")
            return []
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


@app.route('/filter_actors', methods=['POST'])
def filter_actors():
    filter_type = request.form.get('filter_type')
    filter_value = request.form.get('filter_value')

    if filter_type == 'country':
        actors = filter_actors_by_country(filter_value)
    # Можно добавить другие условия для фильтрации актеров по другим критериям, если нужно

    if actors is not None:
        return jsonify(actors)
    else:
        return jsonify({"error": "Произошла ошибка при фильтрации актеров."})




@app.route('/logout')
def logout():
    session.pop('user', None)  # Удаляем пользователя из сессии
    return redirect(url_for('index'))  # Перенаправляем на главную страницу


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user' in session:  # Проверяем, авторизован ли пользователь
        if request.method == 'POST':
            new_password = request.form['new-password']
            confirm_password = request.form['confirm-password']
            username = session['user']  # Получаем имя пользователя из сессии

            if new_password == confirm_password:
                try:
                    mycursor = mydb.cursor()
                    update_query = "UPDATE user SET Password = %s WHERE Login = %s"
                    user_data = (new_password, username)
                    mycursor.execute(update_query, user_data)
                    mydb.commit()
                    mycursor.close()

                    # Отправляем сообщение об успешном изменении пароля
                    return "Пароль успешно изменен"

                except mysql.connector.Error as err:
                    print("Ошибка при выполнении запроса к базе данных:", err)
                    return "Произошла ошибка при изменении пароля."

            else:
                return "Пароли не совпадают. Пожалуйста, попробуйте снова."

        else:
            return "Недопустимый метод запроса"
    else:
        return "Вы не авторизованы"


def get_user_data(username):
    try:
        cursor = mydb.cursor()
        query = "SELECT Login, Email, Password FROM user WHERE Login = %s"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        return user_data
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


@app.route('/user_profile/<username>')
def show_user_profile_for_Admin(username):
    user_data = get_user_data(username)
    if user_data:
        return render_template('user_profile.html', user=user_data)
    else:
        return "Пользователь не найден"


@app.route('/movies')
def get_movies_data():
    try:
        cursor = mydb.cursor()
        query = "SELECT Title, Duration, Year_of_release, Country, Director FROM film"
        cursor.execute(query)
        movies_data = cursor.fetchall()
        cursor.close()
        return render_template('movies.html', movies=movies_data, title='Фильмы')
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return "Произошла ошибка при получении данных о фильмах"


@app.route('/movies')
def movies():
    movies_data = get_movies_data()
    if movies_data:
        return render_template('index.html', movies=movies_data)
    else:
        return "Ошибка получения данных о фильмах"


def get_movie_info(movie_id):
    try:
        cursor = mydb.cursor()
        query = "SELECT f.Title, f.Duration, f.Year_of_release, f.Country, f.Director, d.Description FROM film f LEFT JOIN film_description d ON f.ID_Film = d.ID_Film WHERE f.ID_Film = %s"
        cursor.execute(query, (movie_id,))
        movie_info = cursor.fetchone()
        cursor.close()
        if movie_info:
            movie_dict = {
                'title': movie_info[0],
                'duration': movie_info[1],
                'year': movie_info[2],
                'country': movie_info[3],
                'director': movie_info[4],
                'description': movie_info[5]
            }
            return movie_dict
        else:
            return None
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return None


@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie_info = get_movie_info(movie_id)
    if movie_info:
        return render_template('movie_details.html', movie_info=movie_info)
    else:
        return "Фильм не найден"


@app.route('/get_description/<int:movie_id>')
def get_description(movie_id):
    try:
        cursor = mydb.cursor()
        query = "SELECT Description FROM film_description WHERE ID_Film = %s"
        cursor.execute(query, (movie_id,))
        description = cursor.fetchone()
        cursor.close()
        if description is not None:
            return description[0]  # Возвращаем описание фильма
        else:
            return "Описание отсутствует"
    except mysql.connector.Error as err:
        print("Ошибка при выполнении запроса к базе данных:", err)
        return "Произошла ошибка при получении описания фильма"


if __name__ == '__main__':
    app.run(debug=True)

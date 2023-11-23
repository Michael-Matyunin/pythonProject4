import mysql.connector
from flask import Flask, render_template, request, session, redirect, url_for

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
        insert_query = "INSERT INTO user (Login, Password, Email, rating, Number_Credit_Card, ID_Subscription) VALUES (%s, %s, %s, 'User', 1111, NULL)"
        user_data = (login, password, email)
        mycursor.execute(insert_query, user_data)

        mydb.commit()
        mycursor.close()
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form)  # Print form data for debugging
        login = request.form['loginUsername']  # Updated to match the form field names
        password = request.form['loginPassword']  # Updated to match the form field names

        try:
            mycursor = mydb.cursor()
            query = "SELECT * FROM user WHERE Login = %s AND Password = %s"
            user_data = (login, password)
            mycursor.execute(query, user_data)
            user = mycursor.fetchone()

            # Ваш код для успешной аутентификации пользователя
            if user:
                # Successful login
                session['user'] = login  # Добавляем пользователя в сессию
                return render_template('login_success.html')
            else:
                # Failed login attempt
                return "Login failed. Please check your credentials."

        except mysql.connector.Error as err:
            # Обработка ошибок, например, вывод сообщения об ошибке в консоль для отладки
            print("Ошибка при выполнении запроса к базе данных:", err)
            return "Произошла ошибка при попытке входа."
        finally:
            mycursor.close()


    return render_template('login.html')


# Получение данных из таблицы user
@app.route('/user_profile/<username>')
def show_user_profile(username):
    cursor = mydb.cursor()
    query = "SELECT login, password, email, rating FROM user WHERE Login = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return render_template('user_profile.html', user=user)
    else:
        return "Пользователь не найден"

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

if __name__ == '__main__':
    app.run(debug=True)

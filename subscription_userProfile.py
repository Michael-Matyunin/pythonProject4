

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
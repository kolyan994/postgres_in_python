import psycopg2


def del_tables(cur):  # Удаляет все таблицы
    cur.execute('''
    DROP TABLE phones;
    DROP TABLE clients;
    ''')
    conn.commit()
    return 'Все таблицы удалены'


def create_tables(cur):  # Создает таблицы

    cur.execute('''
    Create table if not exists clients(
    id serial primary key,
    name varchar(60) not null,
    lastname varchar(60) not null,
    email varchar(60));
    ''')

    cur.execute('''
    create table if not exists phones(
    id serial primary key,
    phone varchar(15) not null,
    client_id integer not null references clients(id));
    ''')
    conn.commit()
    return 'Таблицы созданы'


def add_client(cur, name, lastname, email, phones: list = None):  # Добавляет клиента. Можно сразу с телефонами, можно без
    cur.execute('''
    INSERT INTO "clients" ("name", "lastname", "email") VALUES(%s, %s, %s) returning id;
    ''', (name, lastname, email))
    client_id = cur.fetchone()[0]

    if phones:
        for phone in phones:
            add_phone(cur, client_id, phone)
        return 'Клиент с телефоном добавлены'
    return 'Клиент добавлен'


def add_phone(cur, client_id, phone):  # Добавляет телефон существующему клиенту
    cur.execute('''
    INSERT INTO "phones" ("phone", "client_id") VALUES(%s, %s);
    ''', (phone, client_id))
    conn.commit()
    return 'Телефон добавлен'


def change_client(cur, client_id, name=None, last_name=None, email=None, phones=None):  # Меняет любые данные, хоть по одному, хоть сразу все
    if name:
        cur.execute('''
        update clients set name = %s where id = %s;
        ''', (name, client_id))
        conn.commit()
    if last_name:
        cur.execute('''
        update clients set lastname = %s where id = %s;
        ''', (last_name, client_id))
        conn.commit()
    if email:
        cur.execute('''
        update clients set email = %s where id = %s;
        ''', (email, client_id))
        conn.commit()
    if phones:
        delete_phone(cur, client_id)
        for phone in phones:
            add_phone(cur, client_id, phone)
    return 'Данные клиента изменены'


def delete_phone(cur, client_id=None, phone=None):  # Удаляет либо выбранный телефон, либо все телефоны выбранного клиента
    if phone:
        cur.execute('''
        delete from phones where phone = %s;
        ''', (phone,))
        conn.commit()
        return f'Телефон {phone} удален'
    else:
        cur.execute('''
        delete from phones where client_id = %s;
        ''', (client_id,))
        conn.commit()
        return 'Телефоны выбранного клиента удалены'


def delete_client(cur, client_id):  # Целиком удаляет и телефоны и самого клиента
    delete_phone(cur, client_id)
    cur.execute('''
    delete from clients where id = %s;
    ''', (client_id,))
    conn.commit()
    return 'Клиент удален'


def find_client(cur, name=None, last_name=None, email=None, phone=None):  # Находит данные клиента по любым параметрам, вызывает функцию client_info
    if name:
        cur.execute('''
        select * from clients where name = %s;
        ''', (name,))
        fclient = cur.fetchone()
        cur.execute('''
        select phone from phones where client_id = %s;
        ''', (fclient[0],))
        phones = cur.fetchall()

    elif last_name:
        cur.execute('''
        select * from clients where lastname = %s;
        ''', (last_name,))
        fclient = cur.fetchone()
        cur.execute('''
                    select phone from phones where client_id = %s;
                    ''', (fclient[0],))
        phones = cur.fetchall()
    elif email:
        cur.execute('''
        select * from clients where email = %s;
        ''', (email,))
        fclient = cur.fetchone()
        cur.execute('''
                    select phone from phones where client_id = %s;
                    ''', (fclient[0],))
        phones = cur.fetchall()
    else:
        cur.execute('''
        select client_id from phones where phone = %s;
        ''', (phone,))
        client_id = cur.fetchone()[0]
        cur.execute('''
        select * from clients where id = %s;
        ''', (client_id,))
        fclient = cur.fetchone()
        cur.execute('''
                    select phone from phones where client_id = %s;
                    ''', (fclient[0],))
        phones = cur.fetchall()
    return client_info(fclient, phones)


def client_info(client, phones):  # Выводит информацию о клиенте после его поиска
    c_info = {
        'id': client[0],
        'name': client[1],
        'lastname': client[2],
        'email': client[3],
        'phones': phones
    }
    return c_info


with psycopg2.connect(database='clients', user='postgres', password='postgres') as conn:
    with conn.cursor() as cur:

        print(del_tables(cur))  # Удаляем все таблицы
        print(create_tables(cur))  # Создаем их заново
        print(add_client(cur, 'Nikolay', 'Leksin', 'kolyan994@mail.ru'))  # Добавляем первого клиента без телефона
        print(add_client(cur, 'Vika', 'Leksina', 'vikont.t@mail.ru', ['9063668528', '9991112233']))  # Теперь второго с телефонами
        print(add_client(cur, 'Vasya', 'Pupkin', 'vasya@mail.ru', ['99912348678', '9995678216']))  # И третьего
        print(add_phone(cur, '1', '9159340450'))  # Добавляем телефон первому клиенту
        print(add_phone(cur, '1', '9995234578'))  # Теперь еще один
        print(change_client(cur, '2', name='Victoria'))  # Меняем имя второго клиента
        print(change_client(cur, '1', last_name='Lexin', phones=['9991234567', '9997654321']))  # Меняем фамилию и телефоны первого клиента
        print(delete_phone(cur, phone='9997654321'))  # Удаляем телефон
        print(delete_phone(cur, '3'))  # Удаляем все телефоны третьего клиента
        print(delete_client(cur, '3'))  # Удаляем третьего клиента
        print(find_client(cur, phone='9063668528'))  # Ищем клиента по телефону
        print(find_client(cur, email='kolyan994@mail.ru'))  # Ищем клиента по email

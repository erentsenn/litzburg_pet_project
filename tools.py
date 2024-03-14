import sqlite3
from datetime import datetime
from configparser import ConfigParser
import app_logger
import random
logger = app_logger.get_logger(__name__)

conn = sqlite3.connect('target.db')
cur = conn.cursor()
config = ConfigParser()
config.read('credentials/config.ini')
#-----------------------------------------------------------------------------------------------------------filter part
#-----------------------------------------------------------------------------------------------------------filter part
#-----------------------------------------------------------------------------------------------------------filter part
def find_admin(username: str) -> bool:
    info = cur.execute('SELECT * FROM admins WHERE username=?', (username,))
    if info.fetchone() is None:
        logger.info(f'{username} is not admin')
        return False
    else:
        logger.info(f'{username} is admin')
        return True


#-----------------------------------------------------------------------------------------------------------mailing part
#-----------------------------------------------------------------------------------------------------------mailing part
#-----------------------------------------------------------------------------------------------------------mailing part
def get_matches_sqlite():
    cur.execute(
        f"""
                SELECT id, first_player, second_player FROM matches WHERE result=? 
                """, (0,)
    )
    res = []
    for row in cur.fetchall():
        res.append(list(row))
    return res



def get_match_to_bot(id):
    cur.execute(
        f"""
                SELECT first_player, second_player, description FROM matches WHERE id=? 
                """, (id,)
    )
    res = []
    for row in cur.fetchall():
        r = list(row)
    return f'{r[0]} - {r[1]}. {r[2]}'


def get_users():
    cur.execute(
        f"""
                SELECT chat_id FROM users
                """
                )
    res = []
    for row in cur.fetchall():
        res.append(row[0])
    return res


#-----------------------------------------------------------------------------------------------------------inserting part
#-----------------------------------------------------------------------------------------------------------inserting part
#-----------------------------------------------------------------------------------------------------------inserting part
def insert_match(first_player, second_player, part, description):
    cur.execute(
            f'''
            INSERT INTO 
            matches (first_player, second_player, part, winner, result, description, time_modified) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (first_player, second_player, part, '0', '0', description, datetime.now().strftime('%H:%M'))
        )
    conn.commit()
    logger.info(f'{first_player} - {second_player} match has successfully inserted in table')


#-----------------------------------------------------------------------------------------------------------winners part
#-----------------------------------------------------------------------------------------------------------winners part
#-----------------------------------------------------------------------------------------------------------winners part
def get_winners(m_id):
    cur.execute(
        f"""
                SELECT first_player, second_player FROM matches WHERE id=? 
                """, (m_id,)
    )
    for row in cur.fetchall():
        return list(row)
    


def change_winner(m_id, name):
    cur.execute(
            f"""
            UPDATE matches SET winner='{name}', result={1} WHERE id={m_id}
            """)
    conn.commit()


def get_winners_bet(m_id, name):
    cur.execute(
        f"""
        SELECT id, chat_id, username, sum FROM bets WHERE name='{name}' AND match_id={m_id} AND approve={1}
        """
    )
    res = []
    comm_sum = 0
    for row in cur.fetchall():
        res.append(list(row))
        comm_sum += int(list(row)[3])
    return res, comm_sum


def get_sum_lose(m_id, name):
    cur.execute(
        f"""
        SELECT sum FROM bets WHERE name != '{name}' AND match_id={m_id} and approve={1}
        """
    )
    res = []
    for row in cur.fetchall():
        res.append(list(row)[0])
    return sum(res)


#-----------------------------------------------------------------------------------------------------------approvement
#-----------------------------------------------------------------------------------------------------------approvement
#-----------------------------------------------------------------------------------------------------------approvement
def if_in_bets(id):
    info = cur.execute('SELECT id, name, username, sum FROM bets WHERE id=?', (id,))
    b_id = info.fetchone()
    if b_id is None:
        logger.info(f'{id} is not approved')
        return False, []
    else:
        cur.execute(
            f"""
            UPDATE bets SET approve={1} WHERE id='{b_id[0]}'
            """)
        conn.commit()
        logger.info(f'{id} is approved')
        return True, b_id

    

#-----------------------------------------------------------------------------------------------------------user to bet
#-----------------------------------------------------------------------------------------------------------user to bet
#-----------------------------------------------------------------------------------------------------------user to bet

def get_matches_with_players_for_user():
    cur.execute(
        f"""
                SELECT id, first_player, second_player, description FROM matches WHERE result=? 
                """, (0,)
                )
    res = {}
    for row in cur.fetchall():
        res[row[0]] = [row[1], row[2], row[3]]
    return res


def insert_bet(m_id, player, chat_id, username, sum):
    code = ''
    alphabet = 'QWERTYUIOPASDFGHJKLZXCVBNMERENTSEN'
    for _ in range(6):
        code += alphabet[random.randint(0, 26)]
    code += str(datetime.now().minute * datetime.now().second // 77)
    cur.execute(
            f'''
            INSERT INTO 
            bets (id, match_id, name, chat_id, username, sum, kf, approve) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (code, m_id, player, chat_id, username, sum, 1, 0)
            )
    conn.commit()
    logger.info(f'{code} - {username} match has successfully inserted in bets')
    return code


def insert_user(chat_id, username):
    try:
        if not check_user(chat_id):
            cur.execute(f"""insert into users (chat_id, "username")
                                            values (?, ?)""", (chat_id, username))
            conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

    
def check_user(chat_id):
    cur.execute(f"""select username from users where chat_id = {chat_id}""")
    info = cur.fetchone()
    if info:
        return True
    else:
        return False
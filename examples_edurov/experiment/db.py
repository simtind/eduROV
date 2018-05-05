# -*- coding: utf-8 -*-
import argparse
import datetime as dt
import sqlite3
import time
from os import path


class DB:
    db_name = 'data.db'
    db_path = path.join(path.dirname(__file__), db_name)
    table_style = '''
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 5px;
            text-align: left;    
        }'''
    crowd0_order = ['/displays/experiment0.html', '/forms/survey.html',
                    '/displays/experiment1.html', '/forms/survey.html',
                    '/finish.html']
    crowd1_order = ['/displays/experiment1.html', '/forms/survey.html',
                    '/displays/experiment0.html', '/forms/survey.html',
                    '/displays/finish.html']

    def __init__(self):
        if not path.isfile(self.db_path):
            self.createdb()

        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        with open(path.join(path.dirname(__file__), 'table.html'), 'r') as f:
            self.table_base = f.read()

    @classmethod
    def check(cls):
        if path.isfile(cls.db_path):
            print('found file')
        else:
            print('did not find file')

    def actor_dict(self, actor_id):
        self.c.execute(
            """SELECT position, crowd FROM actors WHERE rowid='{}'"""
                .format(actor_id))
        position, crowd = self.c.fetchone()
        return {'position': position,
                'crowd': crowd}

    def next_page(self):
        actor_id = self.last_id()
        dic = self.actor_dict(actor_id)
        current = dic['position']
        crowd = dic['crowd']
        print('Crowd: {}, current: {}'.format(crowd, current))
        if crowd == 0:
            newpage = self.crowd0_order[current + 1]
        else:
            newpage = self.crowd1_order[current + 1]

        with self.conn:
            self.c.execute(
                """UPDATE actors SET position={} 
                WHERE rowid={} LIMIT 1""".format(current + 1, actor_id))
        print('Returning {}'.format(newpage))
        return 'redirect={}'.format(newpage)
        # return 'page={}'.format(newpage)

    @classmethod
    def createdb(cls):
        if not path.isfile(cls.db_path):
            conn = sqlite3.connect(cls.db_path)
            c = conn.cursor()
            c.execute("""CREATE TABLE actors (
                nickname text, 
                age integer,
                gender integer,
                game integer,
                position integer,
                start real,
                starttxt text,
                end real,
                endtxt text,
                crowd integer,
                startexp1 real,
                startexp2 real,
                endexp1 real,
                endexp2 real,
                tothitsexp1 integer,
                tothitsexp2 integer,
                tothits integer,
                valid integer
                )""")
            c.execute("""CREATE TABLE hits (
                actor integer,
                experiment integer,
                button integer,
                time integer
                )""")
            conn.commit()
            conn.close()
            print('Created DB at {}'.format(cls.db_path))
        else:
            raise FileExistsError('{} already exist'.format(cls.db_path))

    def last_id(self):
        self.c.execute("""SELECT rowid FROM actors ORDER BY rowid DESC""")
        return self.c.fetchone()[0]

    def last_experiment(self):
        self.c.execute("""SELECT startexp1, endexp1, startexp2, endexp2 
        FROM actors ORDER BY rowid DESC LIMIT 1""")
        result = self.c.fetchone()
        start1 = result[0]
        end1 = result[1]
        start2 = result[2]
        end2 = result[3]
        if start1 and start2:
            if start1 > start2:
                if not end1:
                    return 1
            else:
                if not end2:
                    return 2
        elif start1 and not end1:
            return 1
        elif start2 and not end2:
            return 2
        return None

    def next_crowd(self):
        self.c.execute("""SELECT * FROM actors WHERE crowd='0'""")
        crowd_0 = len(self.c.fetchall())
        self.c.execute("""SELECT * FROM actors WHERE crowd='1'""")
        crowd_1 = len(self.c.fetchall())
        if crowd_0 > crowd_1:
            return 1
        else:
            return 0

    def new_actor(self, nickname, age, gender, game_consumption):
        timestamp = time.time()
        with self.conn:
            self.c.execute(
                """INSERT INTO actors (nickname, age, gender, game, start, 
                starttxt, crowd, position) 
                VALUES (:nickname, :age, :gender, :game, :start, :starttxt, 
                :crowd, :position)""",
                {'nickname': nickname,
                 'age': int(age),
                 'gender': int(gender),
                 'game': int(game_consumption),
                 'start': timestamp,
                 'starttxt': dt.datetime.fromtimestamp(timestamp).strftime(
                     '%Y-%m-%d %H:%M'),
                 'crowd': self.next_crowd(),
                 'position': -1})
        print('db: new actor created')

    def update_total_hits(self, actor_id):
        self.c.execute(
            """SELECT * FROM hits WHERE actor='{}' AND experiment='1'"""
                .format(actor_id))
        hits_exp_1 = len(self.c.fetchall())
        self.c.execute(
            """SELECT * FROM hits WHERE actor='{}' AND experiment='2'"""
                .format(actor_id))
        hits_exp_2 = len(self.c.fetchall())
        tot_hits = hits_exp_1 + hits_exp_2
        with self.conn:
            data = {'tothitsexp1': hits_exp_1,
                    'tothitsexp2': hits_exp_2,
                    'tothits': tot_hits,
                    'actor_id': actor_id}
            query = """UPDATE actors SET tothitsexp1 = :tothitsexp1, 
            tothitsexp2 = :tothitsexp2, tothits = :tothits 
            WHERE rowid = :actor_id LIMIT 1"""
            self.c.execute(query, data)
        print('db: updated total hits')

    def actor_finished(self, actor_id):
        timestamp = time.time()
        with self.conn:
            data = {'end': timestamp,
                    'endtxt': dt.datetime.fromtimestamp(timestamp)
                        .strftime('%Y-%m-%d %H:%M'),
                    'actor_id': actor_id}
            query = """UPDATE actors SET end = :end, endtxt = :endtxt,
            WHERE rowid = :actor_id LIMIT 1"""
            self.c.execute(query, data)
        print('db: actor finished')

    def experiment_change(self, actor_id, experiment, change):
        experiment = int(experiment)
        timestamp = time.time()
        data = {'actor_id': actor_id, 'time': timestamp}
        if change == 'start':
            with self.conn:
                if experiment == 1:
                    self.c.execute(
                        """UPDATE actors SET startexp1={time} 
                        WHERE rowid={actor_id} LIMIT 1""".format(**data),
                    )
                if experiment == 2:
                    self.c.execute(
                        """UPDATE actors SET startexp2={time} 
                        WHERE rowid={actor_id} LIMIT 1""".format(**data),
                    )
            print('db: experiment started')
        elif change == 'end':
            with self.conn:
                if experiment == 1:
                    self.c.execute(
                        """UPDATE actors SET endexp1={time} 
                        WHERE rowid={actor_id} LIMIT 1""".format(**data),
                    )
                if experiment == 2:
                    self.c.execute(
                        """UPDATE actors SET endexp2={time} 
                        WHERE rowid={actor_id} LIMIT 1""".format(**data),
                    )
            print('db: experiment ended')
        else:
            print('db: not able to process experiment change')

    def new_hit(self, actor_id, button, experiment):
        with self.conn:
            self.c.execute(
                """INSERT INTO hits VALUES (:actor_id, :experiment, :button, 
                :time)""",
                {'actor_id': actor_id,
                 'experiment': int(experiment),
                 'button': int(button),
                 'time': time.time()})
            self.update_total_hits(actor_id)
        print('db: new hit registered')

    def n_actors(self):
        self.c.execute("""SELECT * FROM actors""")
        return str(len(self.c.fetchall()))

    def actor(self, actor_id):
        self.c.execute(
            """SELECT * FROM actors WHERE rowid='{}'""".format(actor_id))
        text = str(self.c.fetchone())
        return text

    def clear_table(self, table):
        with self.conn:
            self.c.execute("DELETE FROM {}".format(table))

    def all_actors_html(self):
        cols_head = ['ID', 'Nickname', 'Group', 'Age', 'Start', 'End',
                     'Start 1', 'End 1', 'Start 2', 'End 2', 'Hits 1',
                     'Hits 2']
        cols = ['rowid', 'nickname', 'crowd', 'age', 'starttxt', 'endtxt',
                'startexp1', 'endexp1', 'startexp2', 'endexp2', 'tothitsexp1',
                'tothitsexp2']
        self.c.execute("""SELECT {} FROM actors""".format(', '.join(cols)))
        table = '<table><tbody>'
        header = '<tr>{}</tr>'.format('<td>{}</td>' * len(cols))
        header = header.format(*cols_head)
        table += header
        for row in self.c.fetchall():
            table += '<tr>{}</tr>'.format(
                ('<td>{}</td>' * len(cols)).format(*row))
        table += '</tbody></table>'
        return self.table_base.format(style=self.table_style, table_html=table)

    def highscore_html(self):
        cols_head = ['Nickname', 'Group', 'Total hits']
        cols = ['nickname', 'crowd', 'tothits']
        self.c.execute("""SELECT {} FROM actors ORDER BY tothits DESC"""
                       .format(', '.join(cols)))
        table = '<table><tbody>'
        header = '<tr>{}</tr>'.format('<td>{}</td>' * len(cols))
        header = header.format(*cols_head)
        table += header
        for row in self.c.fetchall():
            table += '<tr>{}</tr>'.format(
                ('<td>{}</td>' * len(cols)).format(*row))
        table += '</tbody></table>'
        return self.table_base.format(style=self.table_style, table_html=table)


if __name__ == '__main__':
    choices = {'create': DB.createdb, 'check': DB.check}
    parser = argparse.ArgumentParser(
        description='Manage the database')
    parser.add_argument(
        'command',
        choices=choices,
        help='''the command you want to perform''')

    args = parser.parse_args()

    command = choices[args.command]
    command()

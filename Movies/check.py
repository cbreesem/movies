import pandas

from MySQL import MySQL
from PostgreSQL import PostgreSQL

msdb = {'host':'192.168.0.10','user':'myname','password':'myname','database':'im'}
ms = MySQL(msdb)
pgdb = {'host':'localhost','user':'postgres','password':'root','database':'im'}
pg = PostgreSQL(pgdb)

print(ms.tableList)
print(pg.tableList)

fields = pg.getColumns('res_site')
data = pg.select('res_site',fields)

df = pandas.DataFrame(data, columns=fields)
df = df.set_index('id')

fields = ['i_title','i_directors',]
for num,val in df.iterrows():
    where = [
        '`i_imdb_href` = "%s"' % val.imdb,
        '`i_year` = "%s"' % val.year,
        '`d_title` = "%s"' % val.title,
    ]
    r = ms.select('movie_info',[],where)

    print(r)
    if len(r) > 0: break
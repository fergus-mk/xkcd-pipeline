class ComicSQLScripts:
    insert_comic = """INSERT INTO comics (month, num, link, year, news, safe_title, transcript, alt, img, title, day)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
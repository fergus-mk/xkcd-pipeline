class ComicSQLScripts:
    """
    SQL queries related to comic CRUD operations.
    """
    insert_comic = """
    INSERT INTO comics (
        month, num, link, year, news, safe_title,
        transcript, alt, img, title, day
    )
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    select_comic_by_num = "SELECT * FROM comics WHERE num = %s;"

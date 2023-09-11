-- File: initialise.sql
CREATE TABLE IF NOT EXISTS comics (
  id SERIAL PRIMARY KEY,
  month INTEGER,
  num INTEGER,
  link TEXT,
  year INTEGER,
  news TEXT,
  safe_title TEXT,
  transcript TEXT,
  alt TEXT,
  img TEXT,
  title TEXT,
  day INTEGER
);

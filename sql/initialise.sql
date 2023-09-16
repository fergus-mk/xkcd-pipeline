-- Table to store comic-related data
CREATE TABLE IF NOT EXISTS comics (
  id SERIAL PRIMARY KEY, -- Primary id
  month INTEGER NOT NULL, -- Plublication month
  num INTEGER UNIQUE NOT NULL, -- Unique issue number
  link TEXT, -- Link to the comic
  year INTEGER, -- Publication year
  news TEXT, -- Any news assocated with the comic
  safe_title TEXT, -- Comic title safe version 
  transcript TEXT, -- Text for comic
  alt TEXT, -- Alternative text for coiic
  img TEXT, -- Link to image 
  title TEXT, -- Comic title
  day INTEGER NOT NULL -- Publication day
);

-- T1c, PROVIDED: do not edit. The last Week 6 exercise as a CTE chain:
-- movies whose mean rating is at least 0.5 above the mean of their genre,
-- counting only movies with 30 or more ratings. Genre mean here: the mean of
-- the qualifying movies' means.
WITH movie_stats AS (
  SELECT movie_id, AVG(rating) AS movie_mean
  FROM ratings
  GROUP BY movie_id
  HAVING COUNT(*) >= 30),
movie_genre AS (
  SELECT mg.genre_id, s.movie_id, s.movie_mean
  FROM movie_stats AS s
  JOIN movie_genres AS mg USING (movie_id)),
genre_means AS (
  SELECT genre_id, AVG(movie_mean) AS genre_mean
  FROM movie_genre
  GROUP BY genre_id)
SELECT genre_id, movie_id, movie_mean, genre_mean
FROM movie_genre
JOIN genre_means USING (genre_id)
WHERE movie_mean >= genre_mean + 0.5;

-- T1b. How many ratings are above BOTH the user's mean and the movie's mean?
-- Required columns (one row):
--   n_ratings, n_above_both, share_above_both, share_above_both_20plus
-- share_above_both_20plus: the same share, counting only ratings of movies
-- that have at least 20 ratings.
-- Build on T1a in a CTE; filter or count outside it.
--
-- Prediction (commit before running):share_above_both is about 0% to 30%, because a rating must be higher than both averages simultaneously

-- YOUR QUERY HERE

WITH stats AS (
    SELECT
        rating,
        AVG(rating) OVER (PARTITION BY user_id) AS user_mean,
        AVG(rating) OVER (PARTITION BY movie_id) AS movie_mean,
        COUNT(*) OVER (PARTITION BY movie_id) AS movie_count
    FROM ratings
)
SELECT
    COUNT(*) AS n_ratings,
    SUM(CASE WHEN rating > user_mean AND rating > movie_mean THEN 1 ELSE 0 END) AS n_above_both,
    AVG(CASE WHEN rating > user_mean AND rating > movie_mean THEN 1.0 ELSE 0.0 END) AS share_above_both,
    AVG(
        CASE 
            WHEN movie_count >= 20 THEN 
                CASE WHEN rating > user_mean AND rating > movie_mean THEN 1.0 ELSE 0.0 END
            ELSE NULL 
        END
    ) AS share_above_both_20plus
FROM stats;
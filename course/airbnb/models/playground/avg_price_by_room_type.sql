SELECT
  room_type,
  AVG(price) AS avg_price
FROM {{ ref('dim_listings_cleansed') }}
GROUP BY 1

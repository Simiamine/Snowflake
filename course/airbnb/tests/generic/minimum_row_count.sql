{% test minimum_row_count(model, min_row_count) %}
SELECT
    COUNT(*) AS cnt
FROM
    {{ model }}
HAVING
    cnt < {{ min_row_count }}
{% endtest %}
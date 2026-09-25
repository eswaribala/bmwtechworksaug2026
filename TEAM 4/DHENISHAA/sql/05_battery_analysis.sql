SELECT region, AVG(battery_level) AS average_battery_level
FROM telemetry
GROUP BY region
ORDER BY average_battery_level DESC;

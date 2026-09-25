SELECT model, COUNT(*) AS total_vehicles, AVG(battery_capacity_kwh) AS avg_battery_capacity_kwh
FROM vehicle_master
GROUP BY model
ORDER BY total_vehicles DESC;

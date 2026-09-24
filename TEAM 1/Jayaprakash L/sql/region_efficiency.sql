SELECT region, total_distance_km,
total_battery_consumed, overall_efficiency
FROM ev_region_efficiency
ORDER BY overall_efficiency DESC;

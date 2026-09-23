-- TOP 5
SELECT vehicle_id, model, region, overall_efficiency
FROM ev_vehicle_efficiency
ORDER BY overall_efficiency DESC
LIMIT 5;

-- BOTTOM 5
SELECT vehicle_id, model, region, overall_efficiency
FROM ev_vehicle_efficiency
ORDER BY overall_efficiency ASC
LIMIT 5;

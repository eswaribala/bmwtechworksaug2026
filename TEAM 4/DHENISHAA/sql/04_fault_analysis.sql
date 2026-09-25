SELECT fault_code, COUNT(*) AS fault_count
FROM telemetry
GROUP BY fault_code
ORDER BY fault_count DESC;

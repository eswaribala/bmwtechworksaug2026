# 10. Testing Strategy

## Testing goals
- Validate data generation reproducibility
- Validate schema and transformation logic
- Validate missing-value and invalid-value handling
- Validate partition generation and data quality rules

## Stack
- Pytest
- Fixtures
- Deterministic synthetic dataset generation

## Execution
```bash
pytest
pytest --cov=src/bmw_data_lake --cov-report=term-missing
```

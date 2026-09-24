def test_incremental_record_count():
    initial_records = 8
    incremental_records = 4

    final_records = initial_records + incremental_records

    assert final_records == 12


def test_incremental_data_is_not_empty():
    incremental_records = [
        "V009",
        "V010",
        "V011",
        "V012",
    ]

    assert len(incremental_records) > 0
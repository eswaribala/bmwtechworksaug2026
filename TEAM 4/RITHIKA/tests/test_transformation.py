import pandas as pd


def clean_model(model):
    return model.strip().upper()


def test_model_transformation():
    assert clean_model(" iX ") == "IX"


def test_model_uppercase():
    assert clean_model("x5") == "X5"
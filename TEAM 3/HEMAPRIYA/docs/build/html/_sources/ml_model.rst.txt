Machine Learning Model
======================

Overview
--------

The machine learning component predicts the expected sales for the next
month for a specific dealer and BMW model.

The predicted demand is then used by the recommendation engine to
determine whether additional inventory is required.

The machine learning workflow is:

.. code-block:: text

   Historical Data
        |
        v
   Feature Engineering
        |
        v
   Train Multiple Models
        |
        +-------------------+
        |         |         |
        v         v         v
      Linear     Random    XGBoost
    Regression   Forest
        |         |         |
        +---------+---------+
                  |
                  v
          Model Evaluation
                  |
                  v
          Demand Prediction


Prediction Target
-----------------

The target variable is:

``next_month_sales``

The model predicts the number of vehicles expected to be sold during the
following month.

Input Features
--------------

The model uses historical sales, inventory, regional demand, time-based,
and categorical features.

Important feature groups include:

* Recent sales
* Three-month average sales
* Six-month average sales
* Sales growth
* Regional model demand
* Days of inventory
* Inventory turnover
* Month number
* Quarter
* Dealer information
* BMW model information
* Region information

Categorical variables are converted using one-hot encoding.

Training Strategy
-----------------

A chronological train/test split is used instead of a random split.

This is important for demand prediction because the model should be
evaluated on future observations that were not available during training.

Training period:

* July 2021 to December 2024

Testing period:

* January 2025 to November 2025

The training dataset contains 42 monthly periods and the test dataset
contains 11 monthly periods.

Models Evaluated
----------------

Three regression models are evaluated.

Linear Regression
~~~~~~~~~~~~~~~~~

Linear Regression provides a simple baseline model.

It attempts to model the relationship between the input features and
next-month sales using a linear relationship.

Random Forest Regressor
~~~~~~~~~~~~~~~~~~~~~~~

Random Forest is an ensemble model that combines multiple decision trees.

It can capture non-linear relationships between sales, inventory,
regional demand, and other features.

XGBoost Regressor
~~~~~~~~~~~~~~~~~

XGBoost is a gradient boosting algorithm that builds decision trees
sequentially to improve prediction errors from previous trees.

It is used to model more complex relationships between the engineered
features and future demand.

Model Evaluation
----------------

The models are evaluated using three metrics:

Mean Absolute Error
~~~~~~~~~~~~~~~~~~~

MAE measures the average absolute difference between the predicted sales
and the actual sales.

A lower MAE indicates that predictions are closer to the actual values.

Root Mean Squared Error
~~~~~~~~~~~~~~~~~~~~~~~

RMSE measures prediction error while giving greater weight to larger
errors.

A lower RMSE indicates lower prediction error.

R-squared
~~~~~~~~~

R-squared measures how much of the variation in the target variable is
explained by the model.

A higher R-squared indicates that the model explains more of the observed
variation.

Evaluation Results
------------------

The models were evaluated on the chronological test dataset.

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 20

   * - Model
     - MAE
     - RMSE
     - R-squared
   * - Linear Regression
     - 3.4460
     - 4.6324
     - 0.8720
   * - Random Forest
     - 3.2463
     - 4.3699
     - 0.8861
   * - XGBoost
     - 3.1760
     - 4.2790
     - 0.8908

Model Selection
---------------

The model comparison shows that XGBoost produced the lowest MAE and RMSE
among the evaluated models and the highest R-squared value in this
experiment.

Therefore, the trained XGBoost model is used by the recommendation
engine for next-month demand prediction.

The model is saved as:

.. code-block:: text

   artifacts/
   └── best_model.pkl

The feature column configuration used during training is also saved:

.. code-block:: text

   artifacts/
   └── feature_columns.pkl

Inference Process
-----------------

During recommendation, the application:

1. Loads the trained model.
2. Loads the feature column configuration.
3. Loads the historical dealer inventory data.
4. Recreates the required features.
5. Selects the requested dealer and BMW model.
6. Aligns the generated features with the training feature columns.
7. Sends the features to the trained model.
8. Obtains the predicted next-month demand.

The prediction is then passed to the inventory recommendation logic.

Model Limitations
-----------------

The model is trained using synthetic data created specifically for the
project.

Therefore, the evaluation metrics demonstrate the behaviour of the
implemented pipeline but should not be interpreted as measurements of
real-world BMW demand prediction accuracy.

The model should be retrained and re-evaluated when real historical
business data becomes available.

Future Improvements
-------------------

Potential improvements include:

* Hyperparameter tuning
* Additional demand-related features
* More historical data
* Real business data
* Model monitoring
* Prediction drift monitoring
* Automated model retraining
* Comparison with additional forecasting approaches
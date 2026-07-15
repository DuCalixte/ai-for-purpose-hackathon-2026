library(plumber)
library(pins)
library(vetiver)
library(tidymodels)
library(ranger) # Or whatever ML engine you used

# 1. Connect to your consolidated model directory
model_board <- board_folder("../src/saved_champion_models", versioned = FALSE)

model_charges <- vetiver_pin_read(model_board, "delivery_charges_regression")
model_costs   <- vetiver_pin_read(model_board, "delivery_costs_regression")

# 2. Initialize a Plumber router and mount the endpoints
pr() %>%
  vetiver_api(model_charges, path = "/predict_charges") %>%
  vetiver_api(model_costs,   path = "/predict_costs") %>%
  pr_run(port = 8585)

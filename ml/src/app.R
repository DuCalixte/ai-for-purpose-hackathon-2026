library(shiny)
library(bslib)
library(pins)
library(vetiver)
library(dplyr)
library(ggplot2)
library(scales)
library(rmarkdown)
library(gtsummary)
library(gt)
library(readr)

# --- CRITICAL MACHINE LEARNING DEPLOYMENT DEPENDENCIES ---
library(tidymodels)  # Forces the server to understand parsnip and workflows
library(workflows)   # Required to unpack fitted workflows
# Add the specific machine learning engines you used in sparcs_data_analysis.Rmd:
library(ranger)      # Explicitly add if you used Random Forests / Ranger
library(xgboost)     # Explicitly add if you used XGBoost
library(glmnet)      # Explicitly add if you used regularized regression

# ==============================================================================
# 1. INITIALIZATION & MODEL LOADING (Cloud Optimized Deployment)
# ==============================================================================
# Use explicit relative paths to force the cloud server to read from the bundle
model_dir <- file.path(getwd(), "saved_champion_models")

if (!dir.exists(model_dir)) {
  stop(paste("Deployment Error: Folder 'saved_champion_models' not found at:", model_dir))
}

# Define the folder board with explicit arguments for server safety
model_board <- board_folder(path = model_dir, versioned = FALSE)

# Load all 4 models securely from the relative container
model_charges <- vetiver_pin_read(model_board, "delivery_charges_regression")
model_costs   <- vetiver_pin_read(model_board, "delivery_costs_regression")
model_diff    <- vetiver_pin_read(model_board, "delivery_margin_diff_regression")
model_binary  <- vetiver_pin_read(model_board, "delivery_recovery_threshold_classification")

# Load the local dataset required for Tab 2
library(readr)
if (file.exists("sparcs_filtered.csv")) {
  sparcs_filtered <- read_csv("sparcs_filtered.csv")
}
# ==============================================================================
# 2. USER INTERFACE (UI) DESIGN
# ==============================================================================
ui <- page_sidebar(
  title = "Maternal Health Financial Analytics Engine",
  theme = bs_theme(version = 5, bootswatch = "minty"), # Modern, clean aesthetic
  
  # Sidebar: Interactive controls representing your model features
  sidebar = sidebar(
    title = "Patient Case Simulator: Vaginal Delivery",
    width = 325,
    
    # --- CREATOR ATTRIBUTION LAYER ---
    div(
      style = "padding: 8px; background-color: rgba(0,0,0,0.03); border-radius: 4px; margin-bottom: 15px;",
      tags$p(style = "margin: 0; font-size: 0.85rem; color: #6c757d; font-weight: bold;", "Creator:"),
      tags$p(style = "margin: 0; font-size: 0.95rem; font-weight: 500; color: #2c3e50;", "Rose Saint Fleur-Calixte, PhD, PStat®")
    ),
    hr(style = "margin-top: 0;"),
    
    # --- DISCHARGE YEAR TEMPORAL INPUT ---
    sliderInput("discharge_year", "Discharge Calendar Year", 
                min = 2021, max = 2024, value = 2021, step = 1, sep = ""),
    
    hr(),
    
    selectInput("age_group", "Age Group", choices = c("18-29", "30-49")),
    
    # --- DEMOGRAPHIC SELECTORS ---
    selectInput("race", "Patient Race", 
                choices = c("Black/African American", "Multi-racial", "Other Race", "White")),
    
    selectInput("ethnicity", "Patient Ethnicity", 
                choices = c("Multi-ethnic", "Not Span/Hispanic", "Spanish/Hispanic", "Unknown")),
    
    hr(),
    
    selectInput("type_of_admission", "Admission Type", choices = c("Elective", "Emergency", "Urgent")),
    selectInput("hospital_tier", "Hospital Tier", choices = c("Public", "Community", "Private System")),
    selectInput("hospital_county", "Hospital County", choices = c("Bronx", "Kings", "New York", "Queens", "Richmond")),
    
    hr(),
    
    selectInput("apr_severity", "Severity of Illness", 
                choices = c("Minor", "Moderate", "Major", "Extreme")),
    sliderInput("length_of_stay", "Length of Stay (Days)", min = 1, max = 15, value = 2, step = 1),
    
    hr(),
    
    selectInput("payment_typology_1", "Primary Payer Class", 
                choices = c("Blue Cross/Blue Shield", "Private Health Insurance")),
    
    hr(),
    
    # --- EXPORT REPORT BUTTON ---
    downloadButton("download_report", "Generate Simulation Report", class = "btn-success w-100")
  ),
  
  # --- MAIN PANEL MULTI-TAB ARCHITECTURE ---
  navset_card_pill(
    
    # TAB 1: The Core Predictive Dashboard Simulator
    nav_panel(
      title = "Case Prediction Engine",
      icon = bsicons::bs_icon("graph-up-arrow"),
      
      layout_columns(
        fill = FALSE,
        value_box(
          title = "Predicted Total Billed Charges",
          value = textOutput("pred_charges"),
          showcase = bsicons::bs_icon("calculator"),
          theme = "primary"
        ),
        value_box(
          title = "Predicted Hospital Costs",
          value = textOutput("pred_costs"),
          showcase = bsicons::bs_icon("cash-coin"),
          theme = "info"
        ),
        value_box(
          title = "Cost Differential Projection",
          value = textOutput("pred_diff"),
          showcase = bsicons::bs_icon("graph-up"),
          theme = "danger" # Highlights the net margin/spread
        ),
        value_box(
          title = "Probability of Majority Cost Recovery (≥50%)",
          value = textOutput("pred_prob"),
          showcase = bsicons::bs_icon("shield-check"),
          theme = "success"
        )
      ),
      
      layout_columns(
        card(
          card_header("Financial Breakdown Simulation"),
          plotOutput("margin_plot"),
          card_footer("Analytics Engine powered by Vetiver and Parsnip model registries.")
        )
      )
    ),
    
    # TAB 2: The Full Cohort Statistics Summary Matrix
    nav_panel(
      title = "Full Data Summary Matrix",
      icon = bsicons::bs_icon("table"),
      
      card(
        card_header("Maternal Health Clinical & Economic Summary Matrix by Discharge Year"),
        # Optimized layout output for gtsummary/gt elements
        gt_output("full_data_summary_table")
      )
    )
  )
)

# ==============================================================================
# 3. SERVER LOGIC (The Computational Engine)
# ==============================================================================
server <- function(input, output) {
  
  # Reactive dataframe that formats user inputs into the exact shape the models expect
  simulated_case <- reactive({
    tibble(
      discharge_year = as.numeric(input$discharge_year),
      age_group = input$age_group,
      race = input$race,             
      ethnicity = input$ethnicity,    
      length_of_stay = as.numeric(input$length_of_stay),
      apr_severity_of_illness_description = input$apr_severity,
      payment_typology_1 = input$payment_typology_1,
      type_of_admission = input$type_of_admission,
      hospital_county = input$hospital_county,
      hospital_tier = input$hospital_tier
    )
  })
  
  # --- Output 1: Value Box Charges ---
  output$pred_charges <- renderText({
    res <- predict(model_charges, new_data = simulated_case())
    dollar(res$.pred)
  })
  
  # --- Output 2: Value Box Costs ---
  output$pred_costs <- renderText({
    res <- predict(model_costs, new_data = simulated_case())
    dollar(res$.pred)
  })
  
  # --- Output: Value Box Cost Differential ---
  output$pred_diff <- renderText({
    # Pull directly from your dedicated margin difference regression model
    res <- predict(model_diff, new_data = simulated_case())
    diff_val <- res$.pred
    
    dollar(diff_val)
  })
  
  # --- Output 3: Value Box Probabilities ---
  output$pred_prob <- renderText({
    res <- predict(model_binary, new_data = simulated_case(), type = "prob")
    percent(res$.pred_GTE_50)
  })
  
  # --- Output 4: Dynamic Visualization Chart ---
  output$margin_plot <- renderPlot({
    charge_val <- predict(model_charges, new_data = simulated_case())$.pred
    cost_val   <- predict(model_costs, new_data = simulated_case())$.pred
    diff_val   <- predict(model_diff, new_data = simulated_case())$.pred
    
    plot_df <- tibble(
      Metric = c("Billed Charges", "Operational Costs", "Net Remainder Margin"),
      Amount = c(charge_val, cost_val, diff_val)
    )
    
    ggplot(plot_df, aes(x = Metric, y = Amount, fill = Metric)) +
      geom_col(width = 0.5, show.legend = FALSE) +
      scale_y_continuous(labels = label_dollar()) +
      scale_fill_manual(values = c("Billed Charges" = "#56B4E9", 
                                   "Operational Costs" = "#E69F00", 
                                   "Net Remainder Margin" = "#CC79A7")) +
      labs(x = NULL, y = "Estimated Dollar Value ($)") +
      theme_minimal(base_size = 15)
  })
  
  # --- Output 5: Full Cohort Statistics Summary Table ---
  output$full_data_summary_table <- render_gt({
    # Select columns to summarize from your full session pool
    report_data <- sparcs_filtered %>%
      select(
        discharge_year,
        age_group, race, ethnicity,
        type_of_admission, length_of_stay, apr_severity_of_illness_description, 
        apr_risk_of_mortality, apr_medical_surgical_description, hospital_tier, hospital_county,
        payment_typology_1, total_charges, total_costs, 
        cost_to_charge_diff, cost_to_charge_pct, cost_gte_50_pct
      )
    
    # Compile the summary design architecture
    report_data %>%
      tbl_summary(
        by = discharge_year,
        missing = "ifany",
        statistic = list(
          all_continuous() ~ "{mean} ({sd})",  
          all_categorical() ~ "{n} ({p}%)"    
        ),
        digits = all_continuous() ~ 2          
      ) %>%
      add_overall(last = FALSE, col_label = "**Total Pool** (N = {N})") %>%
      add_p(
        test = list(
          all_continuous() ~ "aov",       
          all_categorical() ~ "chisq.test" 
        )
      ) %>%
      bold_labels() %>%
      # Convert the finalized gtsummary to an active gt engine for render
      as_gt()
  })
  
  # --- Output 7: Cloud-Safe Document Report Download Handler ---
  output$download_report <- downloadHandler(
    filename = function() {
      paste0("Maternal_Health_Simulation_Report_", Sys.Date(), ".html")
    },
    content = function(file) {
      # 1. Gather inputs and execute active queries
      current_inputs <- simulated_case() 
      charge_num <- as.numeric(predict(model_charges, new_data = current_inputs)$.pred[[1]])
      cost_num   <- as.numeric(predict(model_costs,   new_data = current_inputs)$.pred[[1]])
      diff_num   <- as.numeric(predict(model_diff,    new_data = current_inputs)$.pred[[1]])
      prob_num   <- as.numeric(predict(model_binary,  new_data = current_inputs, type = "prob")$.pred_GTE_50[[1]])
      
      c_year   <- as.character(current_inputs$discharge_year[[1]])
      c_age    <- as.character(current_inputs$age_group[[1]])
      c_race   <- as.character(current_inputs$race[[1]])
      c_eth    <- as.character(current_inputs$ethnicity[[1]])
      c_adm    <- as.character(current_inputs$type_of_admission[[1]])
      c_tier   <- as.character(current_inputs$hospital_tier[[1]])
      c_county <- as.character(current_inputs$hospital_county[[1]])
      c_sev    <- as.character(current_inputs$apr_severity_of_illness_description[[1]])
      c_los    <- as.character(current_inputs$length_of_stay[[1]])
      c_payer  <- as.character(current_inputs$payment_typology_1[[1]])
      
      # 2. Construct Markdown template script safely directly within memory strings
      rmd_content <- c(
        "---",
        "title: 'Maternal Health Case Simulation Report'",
        "subtitle: 'Vaginal Delivery Financial Projections Engine'",
        "author: 'Generated via Analytics Engine'",
        paste0("date: '", Sys.Date(), "'"),
        "output: html_document",
        "---",
        "",
        "```{r setup, include=FALSE}",
        "knitr::opts_chunk$set(echo = FALSE, message = FALSE, warning = FALSE)",
        "library(scales)",
        "library(ggplot2)",
        "library(tibble)",
        paste0("charge_val <- ", charge_num),
        paste0("cost_val   <- ", cost_num),
        paste0("diff_val   <- ", diff_num),
        paste0("prob_val   <- ", prob_num),
        "```",
        "",
        "### Executive Overview",
        "This clinical and operational evaluation brief was synthesized utilizing predictive modeling frameworks optimized and compiled by **Rose Saint Fleur-Calixte, PhD, PStat®**. The evaluations below present financial risk thresholds based on simulated patient profiles mapped across historical healthcare datasets.",
        "",
        "---",
        "",
        "### 1. Simulated Case Profile Attributes",
        "The configuration matrices selected for this simulation iteration utilize the following parameters:",
        "",
        "| Metric Element | Simulated Parameter Level |",
        "| :--- | :--- |",
        paste0("| **Discharge Calendar Year** | ", c_year, " |"),
        paste0("| **Age Group Profile** | ", c_age, " |"),
        paste0("| **Patient Race Classification** | ", c_race, " |"),
        paste0("| **Patient Ethnicity Profile** | ", c_eth, " |"),
        paste0("| **Admission Priority Path** | ", c_adm, " |"),
        paste0("| **Hospital System Tier** | ", c_tier, " |"),
        paste0("| **Facility Locality (County)** | ", c_county, " |"),
        paste0("| **Severity of Illness (APR)** | ", c_sev, " |"),
        paste0("| **Evaluated Length of Stay** | ", c_los, " Day(s) |"),
        paste0("| **Primary Coverage Class** | ", c_payer, " |"),
        "",
        "---",
        "",
        "### 2. Algorithmic Projections & Financial Impact Metrics",
        "Based on the case metrics specified above, the corresponding champion predictive models have resolved the following expectations:",
        "",
        " * **Predicted Total Billed Charges:** `r dollar(charge_val)`",
        " * **Predicted Net Facility Costs:** `r dollar(cost_val)`",
        " * **Projected Cost Differential Margin:** `r dollar(diff_val)`",
        " * **Probability of Majority Cost Recovery (≥ 50%):** `r percent(prob_val)`",
        "",
        "---",
        "",
        "### 3. Structural Variance Breakdown",
        "",
        "```{r visual_breakdown, fig.width=7, fig.height=4, fig.align='center'}",
        "plot_df <- data.frame(",
        "  Metric = c('Billed Charges', 'Operational Costs', 'Cost Differential'),",
        "  Amount = c(charge_val, cost_val, diff_val),",
        "  stringsAsFactors = FALSE",
        ")",
        "",
        "ggplot(plot_df, aes(x = Metric, y = Amount, fill = Metric)) +",
        "  geom_col(width = 0.4, show.legend = FALSE) +",
        "  scale_y_continuous(labels = label_dollar()) +",
        "  scale_fill_manual(values = c('Billed Charges' = '#56B4E9', ",
        "                               'Operational Costs' = '#E69F00', ",
        "                               'Cost Differential' = '#CC79A7')) +",
        "  labs(title = 'Simulated Balance Summary Pipeline', x = NULL, y = 'Projected Balance ($)') +",
        "  theme_minimal(base_size = 12)",
        "```",
        "",
        "---",
        "*End of Report Briefing.*"
      )
      
      # --- CRITICAL CLOUD ENGINE ROUTING ---
      # 3. Output the raw strings to a temporary file path
      target_rmd <- file.path(tempdir(), "built_simulation_report.Rmd")
      writeLines(rmd_content, target_rmd)
      
      # 4. Compile the asset by explicitly naming the output file destination
      # and enforcing a clean evaluation environment
      rmarkdown::render(
        input = target_rmd,
        output_file = file, # Write directly to Shiny's download stream target
        envir = new.env(parent = globalenv())
      )
    }
  )
}
# ==============================================================================
# 4. RUN THE APPLICATION
# ==============================================================================
shinyApp(ui = ui, server = server)
library(readr)
library(qualityTools)
library(SixSigma)
library(irr)
library(ggplot2)
library(Hmisc)
library(dplyr)
library(tidyr)

r_r_calc <- function(filename, output_image, fig_title, fig_subtitle){
  
  Measurement_Data <- read.csv2(
    filename
    )
  # ICC
  ratings <- t(rbind(
    colMeans(Measurement_Data[Measurement_Data$Mjeritelj == 'A', 3:12]),
    colMeans(Measurement_Data[Measurement_Data$Mjeritelj == 'B', 3:12]), 
    colMeans(Measurement_Data[Measurement_Data$Mjeritelj == 'C', 3:12])
    ))
  icc_data <- icc(
    ratings = ratings,
    model = "twoway",
    type = "consistency",
    unit = "single",
    conf.level = 0.95
    )
  print(icc_data)
  cat("\n\n")
  # Factor with 90 values for operators
  operators <- factor(rep(Measurement_Data$Mjeritelj, each=10))
  # View(operators)
  # Each O-ring (10 parts) is measured 3 times by 3 operators
  o_ring <- factor(rep(rep(1:10, each=3), 3))
  # View(o_ring)
  # 10 parts are measured 3 times each
  run_num <- factor(rep(Measurement_Data$Broj.mjerenja, 10))
  # View(run_num)
  # Measurements
  measurements <- c(
    as.numeric(unlist(Measurement_Data[Measurement_Data$Mjeritelj=='A', 3:12])),
    as.numeric(unlist(Measurement_Data[Measurement_Data$Mjeritelj=='B', 3:12])),
    as.numeric(unlist(Measurement_Data[Measurement_Data$Mjeritelj=='C', 3:12]))
  )
  # View(measurements)
  # Measurements as data frame
  measurements_df = data.frame(operators, o_ring, run_num, measurements)
  # Graphics device
  png(filename = output_image, width = 1949, height = 2700,
      units = 'px', res = 300)
  # View(measurements_df)
  r_r_study = ss.rr(
    var = measurements,
    part = o_ring,
    appr = operators,
    data = measurements_df,
    sigma = 6,
    main = fig_title,
    sub = fig_subtitle
  )
  # Reset device
  dev.off()
  # r_r_study
}

r_r_autom <- function(filename, output_image, fig_title, fig_subtitle){
  # Load input data from automated measurements
  Measurement_Data_Automated <- read_delim(
    filename, ";", escape_double = FALSE,
    col_types = cols(`Broj mjerenja` = col_factor(
      levels = c("1", "2", "3", "4", "5", "6", "7", "8", "9"))),
    locale = locale(decimal_mark = ","), skip = 1)
  # View(Measurement_Data_Automated)
  # ICC
  icc_data <- icc(
    ratings = t(Measurement_Data_Automated[3:12]),
    model = "twoway",
    type = "consistency",
    unit = "single",
    conf.level = 0.95
    )
  print(icc_data)
  cat("\n\n")
  # Optical measurement system
  mes_syst <- factor(rep('Optical System', 90))
  # Each O-ring (10 parts) is measured 3 times by 3 operators
  o_ring <- factor(rep(1:10, each=9))
  # 10 parts are measured, 9 times each
  run_num <- factor(rep(Measurement_Data_Automated$`Broj mjerenja`, 10))
  # Measurements
  measurements <- as.numeric(unlist(Measurement_Data_Automated[3:12]))
  # Measurements as data.frame
  measurements_df <- data.frame(mes_syst, o_ring, run_num, measurements)
  # Graphics device
  png(filename = output_image, width = 1949, height = 2700,
      units = 'px', res = 300)
  # View(measurements_df)
  r_r_study = ss.rr(
    var = measurements,
    part = o_ring,
    appr = mes_syst,
    data = measurements_df,
    sigma = 6,
    main = fig_title,
    sub = fig_subtitle
  )
  # Reset device
  dev.off()
  # r_r_study
}

icc_comparison <- function(input_manual, input_automated, output_image,
                           fig_title){
  # Load input data from automated measurements
  Measurement_Data_Automated <- read_delim(
    input_automated, ";", escape_double = FALSE,
    col_types = cols(`Broj mjerenja` = col_factor(
      levels = c("1", "2", "3", "4", "5", "6", "7", "8", "9"))),
    locale = locale(decimal_mark = ","), skip = 1)
  # Load input data from manual measurements
  Measurement_Data <- read.csv2(
    input_manual
    )
  # Formatting data in data.frame
  autom_manual <- data.frame(t(rbind(
    colMeans(Measurement_Data[3:12]),
    colMeans(Measurement_Data_Automated[3:12]))),
    row.names = 1:10)
  names(autom_manual) <- c("Manual", "System")
  # ICC
  icc_data <- icc(
    ratings = autom_manual,
    model = "twoway",
    type = "consistency",
    unit = "single",
    conf.level = 0.95
    )
  print(icc_data)
  cat("\n\n")
  # Graphics device
  png(filename = output_image, width = 1800, height = 1200,
      units = 'px', res = 300)
  # Plot data
  ggplot(data = autom_manual, aes(x = Manual, y = System)) + 
    geom_point(shape=1) + 
    geom_smooth(aes(color="Linear regression"), method = lm) + 
    geom_abline(aes(slope = 1, intercept = 0, color="Ideal"), 
                show.legend = TRUE) + 
    scale_color_manual(values = c("black", "dodgerblue2")) + 
    labs(color = paste("ICC(C,1) =", round(icc_data$value, 3)),
         title = fig_title)
  ggsave(filename = output_image)
  # Reset device
  dev.off()
  
}

capability_study <- function(input_file){
  # Load input file
  Measurement_Data_Capability <- read.csv2(input_file, row.names=1)
  # O-Ring names
  names(Measurement_Data_Capability) <- 1:10
  # Graphics device for autom_in
  png(filename = "O-Ring_Automated_In_Cp.png", width = 1800, height = 1900,
      units = 'px', res = 300)
  # Capability study for autom_in
  ss.study.ca(as.numeric(Measurement_Data_Capability["autom_in",]),
              LSL = 15.57, USL = 16.03, Target = 15.8,
              f.main = "O-Ring Inner Diameter (System)",
              f.sub = "Six Sigma Capability Analysis")
  dev.off()
  # Graphics device for manual_in
  png(filename = "O-Ring_Manual_In_Cp.png", width = 1800, height = 1900,
      units = 'px', res = 300)
  # Capability study for manual_in
  ss.study.ca(as.numeric(Measurement_Data_Capability["manual_in",]),
              LSL = 15.57, USL = 16.03, Target = 15.8,
              f.main = "O-Ring Inner Diameter (Manual)",
              f.sub = "Six Sigma Capability Analysis")
  dev.off()
  # Graphics device for autom_out
  png(filename = "O-Ring_Automated_Out_Cp.png", width = 1800, height = 1900,
      units = 'px', res = 300)
  # Capability study for autom_out
  ss.study.ca(as.numeric(Measurement_Data_Capability["autom_out",]),
              LSL = 20.21, USL = 20.99, Target = 20.6,
              f.main = "O-Ring Outer Diameter (System)",
              f.sub = "Six Sigma Capability Analysis")
  dev.off()
  # Graphics device for manual_out
  png(filename = "O-Ring_Manual_Out_Cp.png", width = 1800, height = 1900,
      units = 'px', res = 300)
  # Capability study for manual_out
  ss.study.ca(as.numeric(Measurement_Data_Capability["manual_out",]),
              LSL = 20.21, USL = 20.99, Target = 20.6,
              f.main = "O-Ring Outer Diameter (Manual)",
              f.sub = "Six Sigma Capability Analysis")
  dev.off()
  # Graphics device for manual_thick
  png(filename = "O-Ring_Manual_Thick_Cp.png", width = 1800, height = 1900,
      units = 'px', res = 300)
  # Capability study for manual_thick
  ss.study.ca(as.numeric(Measurement_Data_Capability["manual_thick",]),
              LSL = 2.32, USL = 2.48, Target = 2.4,
              f.main = "O-Ring Cross-section (Manual)",
              f.sub = "Six Sigma Capability Analysis")
  dev.off()
}

calib_sensitivity <- function(input_file, fig_title, output_image){
  # Load input data from automated measurements
  Measurement_Data_Automated <- read_delim(
    input_file, ";", escape_double = FALSE,
    col_types = cols(`Broj mjerenja` = col_factor(
      levels = c("1", "2", "3", "4", "5", "6", "7", "8", "9"))),
    locale = locale(decimal_mark = ","), skip = 1)
  # Remove column from data.frame
  Measurement_Data_Automated <- subset(
    Measurement_Data_Automated, select = -`Broj mjerenja`)
  # Change column name
  names(Measurement_Data_Automated)[1] <- "mm/px ratio"
  # Correlation matrix
  print("Correlation Matrix")
  corr_mat <- rcorr(as.matrix(Measurement_Data_Automated), type = "pearson")
  Pearson_R <- matrix(rep(corr_mat$r[1,2:11], each=9))
  print(corr_mat$r[1,])
  print(corr_mat$P[1,])
  cat("\n\n")
  # Linear regression coefficients
  reg_coeff <- c()
  for (ring in colnames(Measurement_Data_Automated[2:11])){
    print(ring)
    linMod <- lm(Measurement_Data_Automated[[ring]] ~ `mm/px ratio`,
                 data = Measurement_Data_Automated)
    print(linMod)
    reg_coeff <- cbind(reg_coeff, linMod$coefficients[2])
  }
  reg_coeff <- round(reg_coeff, 2) %>% rep(each=9) %>% factor()
  # Graphics device
  png(filename = output_image, width = 1949, height = 2700,
      units = 'px', res = 300)
  # Plot data in grid
  Measurement_Data_Automated %>%
    gather(-`mm/px ratio`, key = "var", value = "value") %>% 
    ggplot(aes(x = `mm/px ratio`, y = value)) + 
    geom_point(aes(fill = reg_coeff), shape=21, size = 3) +
    geom_smooth(aes(color = Pearson_R), method = lm) +
    scale_fill_viridis_d(name = "Sensitivity", option = "D") +
    scale_color_continuous(name="Pearson's r") +
    facet_wrap(~var, ncol = 2, scales = "fixed") +
    xlab("mm/px ratio [mm/px]") +
    ylab("Diameter [mm]") +
    labs(title = fig_title, subtitle = "Calibration sensitivity")
  # Save data
  ggsave(filename = output_image)
  # Reset device
  dev.off()
}

print('ICC and R&R for O-ring cross-section')
r_r_calc(filename = "Measurement_Data_Thick.csv",
         output_image = "O-Ring_Thick_R_R.png",
         fig_subtitle = "Six Sigma O-Ring R&R",
         fig_title = "O-Ring Cross-section (Micrometer)")

print('ICC and R&R for O-ring inner diameter')
r_r_calc(filename = "Measurement_Data_In.csv",
         output_image = "O-Ring_In_R_R.png",
         fig_subtitle = "Six Sigma O-Ring R&R",
         fig_title = "O-Ring Inner Diameter (Micrometer)")

print('ICC and R&R for O-ring outer diameter')
r_r_calc(filename = "Measurement_Data_Out.csv",
         output_image = "O-Ring_Out_R_R.png",
         fig_subtitle = "Six Sigma O-Ring R&R",
         fig_title = "O-Ring Outer Diameter (Micrometer)")

print('ICC and R&R for O-ring automated outer diameter')
r_r_autom(filename = "Measurement_Data_Automated_Out.csv",
          output_image = "O-Ring_Automated_Out_R_R.png",
          fig_subtitle = "Six Sigma O-Ring R&R",
          fig_title = "O-Ring Outer Diameter (System)")

print('ICC and R&R for O-ring automated inner diameter')
r_r_autom(filename = "Measurement_Data_Automated_In.csv",
          output_image = "O-Ring_Automated_In_R_R.png",
          fig_subtitle = "Six Sigma O-Ring R&R",
          fig_title = "O-Ring Inner Diameter (System)")

print('ICC (System - Manual) for O-ring inner diameter')
icc_comparison(input_manual = "Measurement_Data_In.csv",
               input_automated = "Measurement_Data_Automated_In.csv",
               output_image = "O-Ring_Comparison_In.png",
               fig_title = "O-Ring Inner Diameter comparison")

print('ICC (System - Manual) for O-ring outer diameter')
icc_comparison(input_manual = "Measurement_Data_Out.csv",
               input_automated = "Measurement_Data_Automated_Out.csv",
               output_image = "O-Ring_Comparison_Out.png",
               fig_title = "O-Ring Outer Diameter comparison")

print("Capability study")
capability_study(input_file = "Measurement_Data_Capability.csv")

print("Calibration (System) sensitivity O-ring Outer Diameter")
calib_sensitivity(input_file = "Measurement_Data_Automated_Out.csv",
                  fig_title = "O-ring Outer Diameter",
                  output_image = "O-Ring_Calibration_Sensitivity_Out.png")

print("Calibration (System) sensitivity O-ring Inner Diameter")
calib_sensitivity(input_file = "Measurement_Data_Automated_In.csv",
                  fig_title = "O-ring Inner Diameter",
                  output_image = "O-Ring_Calibration_Sensitivity_In.png")
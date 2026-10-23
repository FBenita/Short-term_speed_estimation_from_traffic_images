library(ggplot2)
library(tidyr)
library(dplyr)
library(viridis)

cat("\014") 
rm(list = ls())
graphics.off()


####################################################
####################################################
###############    Mask R-CNN Image Segmentation
####################################################
####################################################


# The palette with grey:
cbp1 <- c("#999999", "#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")


################################################################
####################    Plots weekdays
################################################################

df_n<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles\\b_WoodlandsAverage_vehicles_per_Time_on_weekdays.csv", header = T)
df_n <- df_n[,c("Time", "total_car", "total_truck", "total_bus")]
df_n$direction <- "Direction: North"
df_n <- df_n %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df_s<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles\\b_PIEAverage_vehicles_per_Time_on_weekdays.csv", header = T)
df_s <- df_s[,c("Time", "total_car", "total_truck", "total_bus")]
df_s$direction <- "Direction: South"
df_s <- df_s %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df <- rbind(df_n, df_s)


df_long <- gather(df, key = "Vehicle", value = "Value", Car, Truck, Bus)
df_long$Vehicle <- factor(df_long$Vehicle, levels = c("Bus", "Truck", "Car"))

df_sum <- df_long
#df_sum$Hour <- substr(df_sum$Time, 1, 2)
#df_sum <- aggregate(Value ~ Hour + direction + Vehicle, data = df_sum, sum)
#df_sum <- df_sum[df_sum$Hour != "04", ]

df_sum <- df_sum %>%
  mutate(Hour = substr(Time, 1, 2)) %>%
  group_by(Hour, direction, Vehicle) %>%
  summarise(Value = sum(Value)) %>%
  filter(Hour != "04")
df_sum$Vehicle <- factor(df_sum$Vehicle, levels = c("Bus", "Truck", "Car"))


#Create density plot
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekdays_MaskR-CNN.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_long, aes(Value, fill = Vehicle, colour = Vehicle)) +
  geom_density(alpha = 0.1) + scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  labs(x = "Number of vehicles",
       y = "Density") +
  facet_grid(direction ~ ., scales = "free_y") + 
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  



png("Traffic_on_weekdays_per_hour_MaskR-CNN.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_sum, aes(x = Hour, y = Value, fill = Vehicle)) +
  geom_bar(stat = "identity", position = "stack") + scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  facet_grid(direction ~ ., scales = "free_y") +
  labs(x = "Hour", y = "Average number of vehicles") +
  theme_classic(base_size = 22) +
  coord_cartesian(ylim = c(0, 2000))
plot
print(plot)
dev.off()
graphics.off()  


df_speed <- read.csv("C:\\Users\\Traffic_Cameras\\Results\\Google_avg_speed\\march_june_avg_speed_per_route 1.csv", header = T)
df_speed$direction <- ifelse( df_speed$Route == "b_PIE", "Direction: South", "Direction: North"  )
df_speed$Hour <- df_speed$hour
df_speed$Hour <- formatC(df_speed$Hour, width = 2, format = "d", flag = "0")
df_speed$hour <- NULL
## Keep only weekdays
df_speed <- subset(df_speed, df_speed$day_type =="weekday")

# Merge dataframes on Hour and direction
df_combined <- merge(df_sum, df_speed, by = c("Hour", "direction"))


# Plotting
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekdays_per_hour_MaskR-CNN_with_speed.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_combined, aes(x = Hour)) +
  # Stacked bar plot
  geom_bar(aes(y = Value, fill = Vehicle), stat = "identity", position = "stack") +
  # Line plot with a second y-axis
  geom_line(aes(y = avg_speed * 10, group = 1), color = "red", size = 1.5) +  # Increased thickness and changed color to red
  # Set the y-axis labels and colors
  scale_fill_manual(values = cbp1) +
  scale_color_manual(values = "red") +
  # Use facet_grid for separating by direction
  facet_grid(direction ~ ., scales = "free_y") +
  # Set axis labels and plot title
  labs(x = "Hour", y = "Average number of vehicles", color = "Average Speed (in units)") +  # Updated y-axis label
  # Apply classic theme
  theme_classic(base_size = 12) +
  # Set y-axis limits for the bar plot
  coord_cartesian(ylim = c(0, 2000)) +
  # Add a second y-axis with appropriate labels
  scale_y_continuous(sec.axis = sec_axis(~./10, name = "Average Speed (km/h)")) + 
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  






################################################################
####################    Plots weekends
################################################################

cat("\014") 
rm(list = ls())
graphics.off()

# The palette with grey:
cbp1 <- c("#999999", "#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")



################################################################
####################    Plots weekends
################################################################

df_n<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles\\b_WoodlandsAverage_vehicles_per_Time_on_weekends.csv", header = T)
df_n <- df_n[,c("Time", "total_car", "total_truck", "total_bus")]
df_n$direction <- "Direction: North"
df_n <- df_n %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df_s<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles\\b_PIEAverage_vehicles_per_Time_on_weekends.csv", header = T)
df_s <- df_s[,c("Time", "total_car", "total_truck", "total_bus")]
df_s$direction <- "Direction: South"
df_s <- df_s %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df <- rbind(df_n, df_s)


df_long <- gather(df, key = "Vehicle", value = "Value", Car, Truck, Bus)
df_long$Vehicle <- factor(df_long$Vehicle, levels = c("Bus", "Truck", "Car"))


df_sum <- df_long

df_sum <- df_sum %>%
  mutate(Hour = substr(Time, 1, 2)) %>%
  group_by(Hour, direction, Vehicle) %>%
  summarise(Value = sum(Value)) %>%
  filter(Hour != "04")
df_sum$Vehicle <- factor(df_sum$Vehicle, levels = c("Bus", "Truck", "Car"))

#Create density plot
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekends_MaskR-CNN.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_long, aes(Value, fill = Vehicle, colour = Vehicle)) +
  geom_density(alpha = 0.1) + scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  labs(x = "Number of vehicles",
       y = "Density") +
  facet_grid(direction ~ ., scales = "free_y") +
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  




png("Traffic_on_weekends_per_hour_MaskR-CNN.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_sum, aes(x = Hour, y = Value, fill = Vehicle)) +
  geom_bar(stat = "identity", position = "stack") +
  scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  facet_grid(direction ~ ., scales = "free_y") +
  labs(x = "Hour", y = "Average number of vehicles") +
  theme_classic(base_size = 22) +
  coord_cartesian(ylim = c(0, 2000))
plot
print(plot)
dev.off()
graphics.off()  



df_speed <- read.csv("C:\\Users\\Traffic_Cameras\\Results\\Google_avg_speed\\march_june_avg_speed_per_route 1.csv", header = T)
df_speed$direction <- ifelse( df_speed$Route == "b_PIE", "Direction: South", "Direction: North"  )
df_speed$Hour <- df_speed$hour
df_speed$Hour <- formatC(df_speed$Hour, width = 2, format = "d", flag = "0")
df_speed$hour <- NULL
## Keep only weekend
df_speed <- subset(df_speed, df_speed$day_type =="weekend")

# Merge dataframes on Hour and direction
df_combined <- merge(df_sum, df_speed, by = c("Hour", "direction"))


# Plotting
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekends_per_hour_MaskR-CNN_with_speed.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_combined, aes(x = Hour)) +
  # Stacked bar plot
  geom_bar(aes(y = Value, fill = Vehicle), stat = "identity", position = "stack") +
  # Line plot with a second y-axis
  geom_line(aes(y = avg_speed * 10, group = 1), color = "red", size = 1.5) +  # Increased thickness and changed color to red
  # Set the y-axis labels and colors
  scale_fill_manual(values = cbp1) +
  scale_color_manual(values = "red") +
  # Use facet_grid for separating by direction
  facet_grid(direction ~ ., scales = "free_y") +
  # Set axis labels and plot title
  labs(x = "Hour", y = "Average number of vehicles", color = "Average Speed (in units)") +  # Updated y-axis label
  # Apply classic theme
  theme_classic(base_size = 12) +
  # Set y-axis limits for the bar plot
  coord_cartesian(ylim = c(0, 2000)) +
  # Add a second y-axis with appropriate labels
  scale_y_continuous(sec.axis = sec_axis(~./10, name = "Average Speed (km/h)")) + 
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  




####################################################
####################################################
###############    Trnasformer
####################################################
####################################################



cat("\014") 
rm(list = ls())
graphics.off()


# The palette with grey:
cbp1 <- c("#999999", "#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")


################################################################
####################    Plots weekdays
################################################################

df_n<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles_transformer\\b_WoodlandsAverage_vehicles_per_Time_on_weekdays_Transformer.csv", header = T)
df_n <- df_n[,c("Time", "total_car", "total_truck", "total_bus")]
df_n$direction <- "Direction: North"
df_n <- df_n %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df_s<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles_transformer\\b_PIEAverage_vehicles_per_Time_on_weekdays_Transformer.csv", header = T)
df_s <- df_s[,c("Time", "total_car", "total_truck", "total_bus")]
df_s$direction <- "Direction: South"
df_s <- df_s %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df <- rbind(df_n, df_s)


df_long <- gather(df, key = "Vehicle", value = "Value", Car, Truck, Bus)
df_long$Vehicle <- factor(df_long$Vehicle, levels = c("Bus", "Truck", "Car"))

df_sum <- df_long
#df_sum$Hour <- substr(df_sum$Time, 1, 2)
#df_sum <- aggregate(Value ~ Hour + direction + Vehicle, data = df_sum, sum)
#df_sum <- df_sum[df_sum$Hour != "04", ]

df_sum <- df_sum %>%
  mutate(Hour = substr(Time, 1, 2)) %>%
  group_by(Hour, direction, Vehicle) %>%
  summarise(Value = sum(Value)) %>%
  filter(Hour != "04")
df_sum$Vehicle <- factor(df_sum$Vehicle, levels = c("Bus", "Truck", "Car"))


#Create density plot
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekdays_Transformer.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_long, aes(Value, fill = Vehicle, colour = Vehicle)) +
  geom_density(alpha = 0.1) + scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  labs(x = "Number of vehicles",
       y = "Density") +
  facet_grid(direction ~ ., scales = "free_y") + 
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  



png("Traffic_on_weekdays_per_hour_transformer.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_sum, aes(x = Hour, y = Value, fill = Vehicle)) +
  geom_bar(stat = "identity", position = "stack") + scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  facet_grid(direction ~ ., scales = "free_y") +
  labs(x = "Hour", y = "Average number of vehicles") +
  theme_classic(base_size = 22) #+
  #coord_cartesian(ylim = c(0, 2000))
plot
print(plot)
dev.off()
graphics.off()  

df_speed <- read.csv("C:\\Users\\Traffic_Cameras\\Results\\Google_avg_speed\\march_june_avg_speed_per_route 1.csv", header = T)
df_speed$direction <- ifelse( df_speed$Route == "b_PIE", "Direction: South", "Direction: North"  )
df_speed$Hour <- df_speed$hour
df_speed$Hour <- formatC(df_speed$Hour, width = 2, format = "d", flag = "0")
df_speed$hour <- NULL
## Keep only weekdays
df_speed <- subset(df_speed, df_speed$day_type =="weekday")

# Merge dataframes on Hour and direction
df_combined <- merge(df_sum, df_speed, by = c("Hour", "direction"))


# Plotting
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekdays_per_hour_Transformer_with_speed.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_combined, aes(x = Hour)) +
  # Stacked bar plot
  geom_bar(aes(y = Value, fill = Vehicle), stat = "identity", position = "stack") +
  # Line plot with a second y-axis
  geom_line(aes(y = avg_speed * 10, group = 1), color = "red", size = 1.5) +  # Increased thickness and changed color to red
  # Set the y-axis labels and colors
  scale_fill_manual(values = cbp1) +
  scale_color_manual(values = "red") +
  # Use facet_grid for separating by direction
  facet_grid(direction ~ ., scales = "free_y") +
  # Set axis labels and plot title
  labs(x = "Hour", y = "Average number of vehicles", color = "Average Speed (in units)") +  # Updated y-axis label
  # Apply classic theme
  theme_classic(base_size = 12) +
  # Set y-axis limits for the bar plot
  coord_cartesian(ylim = c(0, 2000)) +
  # Add a second y-axis with appropriate labels
  scale_y_continuous(sec.axis = sec_axis(~./10, name = "Average Speed (km/h)")) + 
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  


################################################################
####################    Plots weekends
################################################################

cat("\014") 
rm(list = ls())
graphics.off()

# The palette with grey:
cbp1 <- c("#999999", "#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")



################################################################
####################    Plots weekdays
################################################################

df_n<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles_transformer\\b_WoodlandsAverage_vehicles_per_Time_on_weekends_Transformer.csv", header = T)
df_n <- df_n[,c("Time", "total_car", "total_truck", "total_bus")]
df_n$direction <- "Direction: North"
df_n <- df_n %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df_s<- read.csv("C:\\Users\\Traffic_Cameras\\Data\\count_of_vehicles_transformer\\b_PIEAverage_vehicles_per_Time_on_weekends_Transformer.csv", header = T)
df_s <- df_s[,c("Time", "total_car", "total_truck", "total_bus")]
df_s$direction <- "Direction: South"
df_s <- df_s %>%
  rename(Car = total_car, Truck = total_truck, Bus = total_bus)

df <- rbind(df_n, df_s)


df_long <- gather(df, key = "Vehicle", value = "Value", Car, Truck, Bus)
df_long$Vehicle <- factor(df_long$Vehicle, levels = c("Bus", "Truck", "Car"))


df_sum <- df_long

df_sum <- df_sum %>%
  mutate(Hour = substr(Time, 1, 2)) %>%
  group_by(Hour, direction, Vehicle) %>%
  summarise(Value = sum(Value)) %>%
  filter(Hour != "04")
df_sum$Vehicle <- factor(df_sum$Vehicle, levels = c("Bus", "Truck", "Car"))

#Create density plot
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekends_transformer.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_long, aes(Value, fill = Vehicle, colour = Vehicle)) +
  geom_density(alpha = 0.1) + scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  labs(x = "Number of vehicles",
       y = "Density") +
  facet_grid(direction ~ ., scales = "free_y") +
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  




png("Traffic_on_weekends_per_hour_transformer.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_sum, aes(x = Hour, y = Value, fill = Vehicle)) +
  geom_bar(stat = "identity", position = "stack") +
  scale_colour_manual(values = cbp1)+ scale_fill_manual(values = cbp1)+ 
  facet_grid(direction ~ ., scales = "free_y") +
  labs(x = "Hour", y = "Average number of vehicles") +
  theme_classic(base_size = 22) #+
  #coord_cartesian(ylim = c(0, 2000))
plot
print(plot)
dev.off()
graphics.off()  


df_speed <- read.csv("C:\\Users\\Traffic_Cameras\\Results\\Google_avg_speed\\march_june_avg_speed_per_route 1.csv", header = T)
df_speed$direction <- ifelse( df_speed$Route == "b_PIE", "Direction: South", "Direction: North"  )
df_speed$Hour <- df_speed$hour
df_speed$Hour <- formatC(df_speed$Hour, width = 2, format = "d", flag = "0")
df_speed$hour <- NULL
## Keep only weekend
df_speed <- subset(df_speed, df_speed$day_type =="weekend")

# Merge dataframes on Hour and direction
df_combined <- merge(df_sum, df_speed, by = c("Hour", "direction"))


# Plotting
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Traffic_on_weekend_per_hour_Transformer_with_speed.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(df_combined, aes(x = Hour)) +
  # Stacked bar plot
  geom_bar(aes(y = Value, fill = Vehicle), stat = "identity", position = "stack") +
  # Line plot with a second y-axis
  geom_line(aes(y = avg_speed * 10, group = 1), color = "red", size = 1.5) +  # Increased thickness and changed color to red
  # Set the y-axis labels and colors
  scale_fill_manual(values = cbp1) +
  scale_color_manual(values = "red") +
  # Use facet_grid for separating by direction
  facet_grid(direction ~ ., scales = "free_y") +
  # Set axis labels and plot title
  labs(x = "Hour", y = "Average number of vehicles", color = "Average Speed (in units)") +  # Updated y-axis label
  # Apply classic theme
  theme_classic(base_size = 12) +
  # Set y-axis limits for the bar plot
  coord_cartesian(ylim = c(0, 2000)) +
  # Add a second y-axis with appropriate labels
  scale_y_continuous(sec.axis = sec_axis(~./10, name = "Average Speed (km/h)")) + 
  theme_classic(base_size = 22)
plot
print(plot)
dev.off()
graphics.off()  




####################################################
####################################################
###############    Boxplot Mask R-CNN Image Segmentation accuracy
####################################################
####################################################

cat("\014") 
rm(list = ls())
graphics.off()




df_rcnn<- read.csv("C:\\Users\\Traffic_Cameras\\Results\\Accuracy\\maskrcnn_march_june_vehicle_summary.csv", header = T)
df_rcnn$Segmentation_pixels <- NULL
table(df_rcnn$Detection_Class)




df_trans<- read.csv("C:\\Users\\Traffic_Cameras\\Results\\Accuracy\\transformer_march_june_vehicle_summary.csv", header = T)
table(df_trans$Detection_Class)


# Add a new column to each dataframe indicating the source
df_rcnn$Source <- "Mask R-CNN"
df_trans$Source <- "DETR"

df_rcnn_more_than_point3 <- subset(df_rcnn, df_rcnn$Detection_Score>0.3)
df_rcnn_more_than_point3$Source <- "Mask R-CNN (Det. acc. >= 0.3)"
# Combine the dataframes
combined_df <- rbind(df_rcnn, df_rcnn_more_than_point3,df_trans)
combined_df$direction <- ifelse( combined_df$Route == "b_PIE", "Direction: South", "Direction: North"  )


combined_df$Source <- factor(combined_df$Source, levels = c("Mask R-CNN", "Mask R-CNN (Det. acc. >= 0.3)", "DETR"))


# Define a custom color palette
custom_palette <- c("#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3")

# Create a boxplot
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Boxplots_with_acc.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(combined_df, aes(x = Source, y = Detection_Score, fill = direction)) +
  geom_boxplot() +
  scale_fill_manual(values = custom_palette) +  # Set custom color palette
  xlab("") + ylab("Detection Score") + 
  theme_minimal() +
  theme_classic(base_size = 22) +
  theme(legend.position="bottom") +  # Place legend at the bottom
  guides(fill = guide_legend(title = NULL))  # Remove the legend title
plot
print(plot)
dev.off()
graphics.off()  





####################################################
####################################################
###############    Boxplot Forecasting deviations
####################################################
####################################################

cat("\014") 
rm(list = ls())
graphics.off()

##### Mask R-CNN
df_south_rcnn <- read.csv("C:\\Users\\Traffic_Cameras\\Data\\Deviations_Forecasting\\b_PIE_rcnn.csv", header = T)
df_north_rcnn <- read.csv("C:\\Users\\Traffic_Cameras\\Data\\Deviations_Forecasting\\b_Woodlands_rcnn.csv", header = T)
d <-rbind(df_north_rcnn, df_south_rcnn)


rcnn_lstm_tplus1<- data.frame(
  value = d$lstm_m2_1_diff,
  x = "t+1 (5 min)",
  Approach = "LSTM",
  Method = "Mask R-CNN"
)

rcnn_lstm_tplus3<- data.frame(
  value = d$lstm_m2_3_diff,
  x = "t+3 (15 min)",
  Approach = "LSTM",
  Method = "Mask R-CNN"
)

rcnn_lstm_tplus6<- data.frame(
  value = d$lstm_m2_6_diff,
  x = "t+6 (30 min)",
  Approach = "LSTM",
  Method = "Mask R-CNN"
)


rcnn_xgb_plus1<- data.frame(
  value = d$xgb_m2_1_diff,
  x = "t+1 (5 min)",
  Approach = "XGB",
  Method = "Mask R-CNN"
)

rcnn_xgb_plus3<- data.frame(
  value = d$xgb_m2_1_diff,
  x = "t+3 (15 min)",
  Approach = "XGB",
  Method = "Mask R-CNN"
)

rcnn_xgb_plus6<- data.frame(
  value = d$xgb_m2_6_diff,
  x = "t+6 (30 min)",
  Approach = "XGB",
  Method = "Mask R-CNN"
)

rcnn <- rbind(rcnn_lstm_tplus1, rcnn_lstm_tplus3, rcnn_lstm_tplus6, rcnn_xgb_plus1, rcnn_xgb_plus3, rcnn_xgb_plus6)




##### Detr

df_south_rcnn <- read.csv("C:\\Users\\Traffic_Cameras\\Data\\Deviations_Forecasting\\b_PIE_transformer.csv", header = T)
df_north_rcnn <- read.csv("C:\\Users\\Traffic_Cameras\\Data\\Deviations_Forecasting\\b_Woodlands_transformer.csv", header = T)
d <-rbind(df_north_rcnn, df_south_rcnn)

deter_lstm_tplus1<- data.frame(
  value = d$lstm_m2_1_diff,
  x = "t+1 (5 min)",
  Approach = "LSTM",
  Method = "DETR"
)

deter_lstm_tplus3<- data.frame(
  value = d$lstm_m2_3_diff,
  x = "t+3 (15 min)",
  Approach = "LSTM",
  Method = "DETR"
)

deter_lstm_tplus6<- data.frame(
  value = d$lstm_m2_6_diff,
  x = "t+6 (30 min)",
  Approach = "LSTM",
  Method = "DETR"
)


deter_xgb_plus1<- data.frame(
  value = d$xgb_m2_1_diff,
  x = "t+1 (5 min)",
  Approach = "XGB",
  Method = "DETR"
)

deter_xgb_plus3<- data.frame(
  value = d$xgb_m2_1_diff,
  x = "t+3 (15 min)",
  Approach = "XGB",
  Method = "DETR"
)

deter_xgb_plus6<- data.frame(
  value = d$xgb_m2_6_diff,
  x = "t+6 (30 min)",
  Approach = "XGB",
  Method = "DETR"
)

deter <- rbind(deter_lstm_tplus1, deter_lstm_tplus3, deter_lstm_tplus6, deter_xgb_plus1, deter_xgb_plus3, deter_xgb_plus6)



d <- rbind( rcnn, deter )

setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Boxplots_forecasting.png", width = 12, height = 8, units = 'in', res = 300)  
plot <- ggplot(d, aes(x=x, y=value, fill=Approach)) + 
      geom_violin() + 
      geom_hline(yintercept = 0, linetype = "dashed", color = "black") +  # Add horizontal line at y = 0
      facet_wrap(~Method) +  
      scale_fill_brewer(palette = "Set3")  + # Using the Set1 palette from RColorBrewer
      scale_y_continuous(breaks = c(-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50)) +  # Add breaks on the y-axis
      xlab("Approach") + ylab("Deviation (km/hr)") + 
      theme_minimal() +
      theme_classic(base_size = 22) +
      theme(legend.position="bottom") +  # Place legend at the bottom
      guides(fill = guide_legend(title = NULL))  # Remove the legend title
plot
print(plot)
dev.off()
graphics.off()  






####################################################
####################################################
###############    Mask R-CNN Bar plot Acc>0.3 vs no Filter
####################################################
####################################################


library(readxl)
library(reshape2)

cat("\014") 
rm(list = ls())
graphics.off()

df <- read_excel("C:\\Users\\Traffic_Cameras\\Results\\Tables_paper.xlsx", sheet = "Table rcnn acc")
# Define the columns you want to convert to numeric
cols_to_convert <- c("RMSE", "MAE", "EVS")
# Use mutate_at to convert selected columns to numeric
df <- mutate_at(df, vars(cols_to_convert), as.numeric)

df$Direction <- ifelse(df$Direction=="b_Woodlands", "North", "South")



# Melt the data frame to long format
df_melted <- melt(df, id.vars = c("Direction", "Filter"))

# Create custom color palette
custom_palette <- c("#1f78b4", "#e31a1c")

# Create the barplot using ggplot with custom colors
setwd("C:\\Users\\Traffic_Cameras\\Results\\Figures")
png("Barplot_errors_filtered_accuracy.png", width = 10, height = 6, units = 'in', res = 300)  
plot <- ggplot(df_melted, aes(x = Direction, y = value, fill = Filter)) +
      geom_bar(position = "dodge", stat = "summary", fun = "mean") +
      facet_wrap(~variable, scales = "free_y", nrow = 1) +
      labs(x = "Direction", y = "Value", fill = "") +
      scale_fill_manual(values = custom_palette) +
      theme_minimal() +
      theme_classic(base_size = 22) +
      theme(legend.position="bottom")   # Place legend at the bottom
plot
print(plot)
dev.off()
graphics.off()  


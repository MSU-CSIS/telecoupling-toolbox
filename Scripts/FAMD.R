tool_exec <- function(in_params, out_params)
{
  #### Load Library for Analysis ####
  if (!requireNamespace("FactoMineR", quietly = TRUE))
    install.packages("FactoMineR")
  if (!requireNamespace("missMDA", quietly = TRUE))
    install.packages("missMDA")
  	
  require(FactoMineR)
  require(missMDA)
  
  #### Get Input Parameters ####
  message("Reading Input Parameters...")
  input_table <- in_params[[1]]
  quant_variables <- in_params[[2]]
  qual_variables <- in_params[[3]]
  missing_bool <- in_params[[4]]
  num_fact <- in_params[[5]]
  col_plot <- in_params[[6]]
  
  if (is.null(col_plot))
	col_plot <- "none"
  
  #env = arc.env()
  
  #### Set Output Parameters ####  
  out_pdf <- out_params[[1]]

  #### Import Dataset to Dataframe ####
  message("Creating Dataframe from Input Table...")
  tbl <- arc.open(input_table)
  df <- arc.select(tbl, c(quant_variables, qual_variables))
   
  #### Convert to class FACTOR all Qualitative Variables ####
  which_is_chr <- sapply(df, is.character)
  df[which_is_chr] <- lapply(df[which_is_chr], as.factor) 
   
  #### Remove ALL rows (individuals) that have one or more NAs in qualitative variables #### 
  if (!is.null(qual_variables))
	df <- df[complete.cases(df[(length(quant_variables)+1):ncol(df)]), ]
  
  #### Imputation of NAs (missing) Values ###	
  if (missing_bool)
  {
	if (length(quant_variables) == 1)
	{
		df[is.na(df[,1]), 1] <- median(df[,1], na.rm=TRUE) 
	}else{
		df_sub <- df[ ,1:length(quant_variables)]
		imp_PCA <- imputePCA(df_sub, ncp=1)
		df[ ,1:length(quant_variables)] <- imp_PCA$completeObs
	}
  }

  if (!missing_bool)
	df <- df[complete.cases(df[1:length(quant_variables)]), ]
   
  #### Run Factor Analysis for Mixed Data (FAMD) ####
  message("Running Factor Analysis...")
  tryCatch(
   {
	  res <- FAMD(df, ncp=as.integer(num_fact) ,graph=FALSE)
	  summary(res)   
   })

   tryCatch(
     {
       #wkspath <- env$workspace
	   #print(wkspath)
	   #print(file.path(wkspath,"Report.pdf"))
       pdf("D:/Report_FAMD.pdf")  # <----- CHANGE THIS TO ARCGIS SCRATCH WORKSPACE!!
       par(mfrow=c(2, 2))
       suppressWarnings(plot(res,  choix = "ind", habillage = col_plot))
	   suppressWarnings(plot(res,  choix = "var", habillage = col_plot))
	   suppressWarnings(plot(res,  choix = "quanti", habillage = col_plot))
	   suppressWarnings(plot(res,  choix = "quali", habillage = col_plot))
     }, finally = { dev.off() })  

  return(out_params)
}


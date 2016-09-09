impute_missing <- function(data_frame, quant_variables, qual_variables, ncp=2)
{
    message("Checking for missing data in the dataset...")
	if (any(is.na(data_frame))){
		if (is.null(qual_variables)){
			message("Replacing missing values using PCA-imputed values...")
			if(length(quant_variables) == 2)
			{
				ncp <- 1
				data_frame_sub <- data_frame[ ,1:length(quant_variables)]
				imp_PCA <- imputePCA(data_frame_sub, ncp=ncp)
				data_frame[ ,1:length(quant_variables)] <- imp_PCA$completeObs
			}else{
				data_frame_sub <- data_frame[ ,1:length(quant_variables)]
				imp_PCA <- imputePCA(data_frame_sub, ncp=ncp)
				data_frame[ ,1:length(quant_variables)] <- imp_PCA$completeObs				
			}			
		}else if (is.null(quant_variables)){
			message("Replacing missing values using MCA-imputed values...")
			if(length(qual_variables) == 2)
			{
				ncp <- 1
				data_frame_sub <- data_frame[ ,1:length(qual_variables)]
				imp_MCA <- imputeMCA(data_frame_sub, ncp=ncp)
				data_frame[ ,1:length(qual_variables)] <- imp_MCA$completeObs
			}else{
				data_frame_sub <- data_frame[ ,1:length(qual_variables)]
				imp_MCA <- imputeMCA(data_frame_sub, ncp=ncp)
				data_frame[ ,1:length(qual_variables)] <- imp_MCA$completeObs				
			}				
		}else{
			message("Replacing missing values using FAMD-imputed values...")
			if(length(qual_variables) + length(quant_variables) == 2)
			{
				ncp <- 1
				imp_FAMD <- imputeFAMD(data_frame, ncp=ncp)
				data_frame <- imp_FAMD$completeObs
			}else{
				imp_FAMD <- imputeFAMD(data_frame, ncp=ncp)
				data_frame <- imp_FAMD$completeObs				
			}					
		}
		message("...Missing values replaced!")
	}else{
		message("...No missing values found in the dataset!")
	}
	return(data_frame)
}


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
  quanti_sup <- in_params[[4]]
  quali_sup <- in_params[[5]]
  missing_bool <- in_params[[6]]
  num_fact <- in_params[[7]]
  col_plot <- in_params[[8]]
  col_plot_var <- in_params[[9]]
  ind_select <- in_params[[10]]
  cat_select <- in_params[[11]]
  label_ind <- in_params[[12]]

  if (is.null(col_plot_var))
	col_plot_var <- "none"
	
  #env = arc.env()
  
  #### Set Output Parameters ####  
  out_pdf <- out_params[[1]]
    
  #### Import Dataset to Dataframe ####
  message("Creating Dataframe from Input Table...")
  tbl <- arc.open(input_table)
  df <- arc.select(tbl, c(quant_variables, qual_variables))
 
  #### Convert All Qualitative Variables to class Factor & Remove Records with Any Missing Values ####
  if (!is.null(qual_variables)){
	which_is_quali <- which(names(df) %in% unlist(qual_variables))	
	df[which_is_quali] <- lapply(df[which_is_quali], as.factor)   
	df <- df[complete.cases(df[which_is_quali]), ]
  }
  
  #### Store index of any supplementary variables ####
  if (!is.null(quanti_sup))
	quanti_sup <- which(names(df) %in% unlist(quanti_sup))
  if (!is.null(quali_sup))
	quali_sup <- which(names(df) %in% unlist(quali_sup))
  
  #### Compute Missing Values Using Imputation ####
  if (missing_bool)
	df <- impute_missing(df, quant_variables, qual_variables)
  
  #### Run Factor Analysis for Mixed Data (FAMD) ####
  message("Running Factor Analysis...")
  tryCatch(
   {
	  #### Run PCA if ONLY QUANTITATIVE vars were selected #### 
	  if ( !is.null(quant_variables) ) 
	  {
	    if ( is.null(qual_variables) | (!is.null(quali_sup) && unlist(qual_variables)==unlist(quali_sup)) ){
			warning("You selected only quantitative variables: a PCA will be run!")
			message("Running PCA on quantitative variables...")
			res <- PCA(df, scale=TRUE, quali.sup=quali_sup, quanti.sup=quanti_sup, ncp=as.integer(num_fact), graph=FALSE)
			summary(res)
			dimdesc(res)		
		}
	  }
	  #### Run MCA if ONLY QUALITATIVE vars were selected ####
	  if ( !is.null(qual_variables) )
	  {
	    if ( is.null(quant_variables) | (!is.null(quanti_sup) && unlist(quant_variables)==unlist(quanti_sup)) ){
			warning("You selected only qualitative variables: a MCA will be run!")
			message("Running MCA on qualitative variables...")
			res <- MCA(df, quali.sup=quali_sup, quanti.sup=quanti_sup, ncp=as.integer(num_fact), graph=FALSE)
			summary(res)
			dimdesc(res)		
		}	  
	  }
	  #### Run FAMD otherwise ####
	  if ( !is.null(quant_variables) & !is.null(qual_variables) )
	  {
		res <- FAMD(df, ncp=as.integer(num_fact), graph=FALSE)
		summary(res)	  
	  }
   })
   
   message("Creating Plots for Report...")
   tryCatch(
     {
       #wkspath <- env$workspace
	   #print(wkspath)
	   #print(file.path(wkspath,"Report.pdf"))
       pdf("D:/Report_FAMD.pdf")  # <----- CHANGE THIS TO ARCGIS SCRATCH WORKSPACE!!
	  if ( !is.null(quant_variables) ) 
	  {
	    if ( is.null(qual_variables) | (!is.null(quali_sup) && unlist(qual_variables)==unlist(quali_sup)) ){
			if (label_ind == FALSE){
				label <- c("quali", "var", "quanti.sup")
			}else{
				label <- c("ind", "ind.sup", "quali", "var", "quanti.sup")
			}
			suppressWarnings(plot(res,  choix = "ind", habillage = col_plot, label = label, cex=.7, select = ind_select, selectMod = cat_select))
			suppressWarnings(plot(res,  choix = "var", habillage = col_plot, label = label, cex=.7, select = ind_select, selectMod = cat_select))	
			suppressWarnings(barplot(res$eig[,1], main="Eigenvalues", names.arg=1:nrow(res$eig)))	
		}
	  }
	  #### Run MCA if ONLY QUALITATIVE vars were selected ####
	  if ( !is.null(qual_variables) )
	  {
	    if ( is.null(quant_variables) | (!is.null(quanti_sup) && unlist(quant_variables)==unlist(quanti_sup)) ){
			if (label_ind == FALSE){
				label <- c("var","quali.sup","quanti.sup")
			}else{
				label <- "all"
			}
			suppressWarnings(plot(res,  choix = "ind", habillage = col_plot, label = label, cex=.7, select = ind_select, selectMod = cat_select))
			suppressWarnings(plot(res,  choix = "var", habillage = col_plot, label = label, cex=.7, select = ind_select, selectMod = cat_select))	
			if(!is.null(quanti_sup))
				suppressWarnings(plot(res,  choix = "quanti.sup", habillage = col_plot, label = label, cex=.7, select = ind_select, selectMod = cat_select))	
		}	  
	  }	  
	  #### Run FAMD otherwise ####
	  if ( !is.null(quant_variables) & !is.null(qual_variables) )
	  {
		  suppressWarnings(plot(res,  choix = "ind", habillage = col_plot_var, cex=.7, lab.ind=label_ind, select = ind_select, selectMod = cat_select))
		  suppressWarnings(plot(res,  choix = "var", cex=.7, select = ind_select, selectMod = cat_select))
		  suppressWarnings(plot(res,  choix = "quanti", cex=.7, select = ind_select, selectMod = cat_select))
	  }	  

     }, finally = { dev.off() })  

  return(out_params)
}


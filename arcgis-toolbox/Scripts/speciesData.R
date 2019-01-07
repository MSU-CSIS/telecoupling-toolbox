tool_exec <- function(in_params, out_params)
{
  #### Load library ####
  message("Loading Library...")
  if (!requireNamespace("dismo", quietly = TRUE))
    install.packages("dismo")
  if (!requireNamespace("jsonlite", quietly = TRUE))
    install.packages("jsonlite")
  if (!requireNamespace("sp", quietly = TRUE))
    install.packages("sp")
  
  require(dismo)
  require(jsonlite)
  require(sp)
  
  #### Get input parameters ####
  message("Reading Input Parameters...")
  genus_str <- in_params[[1]]
  species_str <- in_params[[2]]
  ext_file <- in_params[[3]]
  year_range <- in_params[[4]]
  month_range <- in_params[[5]]
  ele_range <- in_params[[6]]
  dep_range <- in_params[[7]]
  
  #### Set output parameters ####
  out_fc <- out_params[[1]]
  
  #USE THESE TWO LINES ONLY WHEN YOU RUN THE SCRIPT IN ARCGIS
  #env <- arc.env()
  #message("good")
  #wkspath <- env$workspace	
  
  
  message("Creating Output Shapefile...")
  #SPDF = SpatialPolygonsDataFrame(tc_systems_spdf, data=tc_systems_df_join)
  #shape_info <- list(type="Polygon", WKT=arc.shapeinfo(arc.shape(tc_systems_df))$WKT)
  
  ### Assign arguments ###
  if (is.null(year_range)== FALSE){
    info <- gbif(genus=genus_str,species=species_str,ext=NULL,args=paste("year=",year_range),geo=TRUE,sp=TRUE,removeZeros=FALSE,download=TRUE,ntries=5,nrecs=300,start=1,end=Inf)
  } else if (is.null(month_range)== FALSE){
    info <- gbif(genus=genus_str,species=species_str,ext=NULL,args=paste("month=",month_range),geo=TRUE,sp=TRUE,removeZeros=FALSE,download=TRUE,ntries=5,nrecs=300,start=1,end=Inf)
  } else if (is.null(ele_range)== FALSE){
    info <- gbif(genus=genus_str,species=species_str,ext=NULL,args=paste("elevation=",ele_range),geo=TRUE,sp=TRUE,removeZeros=FALSE,download=TRUE,ntries=5,nrecs=300,start=1,end=Inf)
  } else if (is.null(dep_range)== FALSE){
    info <- gbif(genus=genus_str,species=species_str,ext=NULL,args=paste("depth=",dep_range),geo=TRUE,sp=TRUE,removeZeros=FALSE,download=TRUE,ntries=5,nrecs=300,start=1,end=Inf)
  } else {info <- gbif(genus=genus_str,species=species_str,ext=NULL,args=NULL,geo=TRUE,sp=TRUE,removeZeros=FALSE,download=TRUE,ntries=5,nrecs=300,start=1,end=Inf)}
  
  message("Creating Output Files...")
  print("Species Report:", quote = FALSE)
  print("Data Extent:", quote = FALSE)
  print(info@bbox)
  print("Data Coordinates:", quote=FALSE)
  print(info@coords)
  
  
  # result = tryCatch({
  #   #pdf(out_pdf)
  #   
  #   suppressWarnings(plot(info))
  #   
  #   
  # }, finally = {
  #   dev.off()
  # }
  # )
 
  #arc.write(path=out_fc, data=info)
  fgdb_path <- file.path(tempdir(), "data.gdb")
  arc.write(file.path(fgdb_path, "fc_pts"),data = info, shape_info=list(type='Point'))
 
  return(out_params)
}

#List of genus and species can be found @
#https://www.gbif.org/occurrence/taxonomy?advanced=1
library(igraph)
library(RColorBrewer)
library(dplyr)
library(sp)



tool_exec <- function(in_params, out_params)
{
  #### Load library ####
  message("Loading Library...")
  if (!requireNamespace("igraph", quietly = TRUE))
    install.packages("igraph")
  if (!requireNamespace("RColorBrewer", quietly = TRUE))
    install.packages("RColorBrewer")
  if (!requireNamespace("dplyr", quietly = TRUE))
    install.packages("dplyr")
  if (!requireNamespace("sp", quietly = TRUE))
    install.packages("sp")
  
  require(igraph)
  require(dplyr)
  require(sp)
  require(RColorBrewer)
  
  #### Get input parameters ####
  message("Reading Input Parameters...")
  input_nodes_table <- in_params[[1]]
  input_link_table <- in_params[[2]]
  input_telecoupling_system <- in_params[[3]]
  clustering_algorithm <- in_params[[4]]
  weight_within <- in_params[[5]]
  weight_between <- in_params[[6]]
  color_set <- in_params[[7]]
  node_size <- in_params[[8]]
  edge_width <- in_params[[9]]
  label_size <- in_params[[10]]
  
  #### Set output parameters ####
  out_pdf <- out_params[[1]]
  out_fc <- out_params[[2]]
  
  # To control thinkness/distances between nodes 
  edge.weights <- function(community, network, weight.within = weight_within, weight.between = weight_between) 
  {
    bridges <- crossing(communities = community, graph = network)
    weights <- ifelse(test = bridges, yes = weight.between, no = weight.within)
    return(weights) 
  }
  
  
  #### Model Input ####
  test.node <- read.csv(file=input_nodes_table, header=T, stringsAsFactors=FALSE, check.names=FALSE)
  test.link <- read.csv(file=input_link_table, header=T, stringsAsFactors=FALSE, check.names=FALSE)
  
  #USE THESE TWO LINES ONLY WHEN YOU RUN THE SCRIPT IN ARCGIS
  env <- arc.env()
  wkspath <- env$workspace	
  
  # change data frame format to igraph format
  test.net <- graph_from_data_frame(d=test.link, vertices=test.node, directed=T)
  
  # create clusters
  message("Creating Clusters...")
  if (clustering_algorithm=="walktrap")
  {
    MyClusters.community <- cluster_walktrap(test.net)
    df <- data.frame(ISO_3_CODE = unique(MyClusters.community)[[4]], cluster_N = as.numeric(unique(MyClusters.community)[[3]]))
  }
  
  if (clustering_algorithm == "spin_glass"){
    MyClusters.community <- cluster_spinglass(test.net)
    df <- data.frame(ISO_3_CODE = unique(MyClusters.community)[[7]], cluster_N = as.numeric(unique(MyClusters.community)[[1]]))
  }
  
  df$ISO_3_CODE <- as.character(df$ISO_3_CODE)
  
  # assign colors to clusters
  NumberOfColors <- length(unique(MyClusters.community))
  Colors <- brewer.pal(NumberOfColors, color_set)
  MyClusters.col <- Colors[membership(MyClusters.community)] 
  
  # change distances among nodes (within the same clusters & between clusters)
  E(test.net)$weight <- edge.weights(MyClusters.community, test.net)
  test.Layout.drl <- layout_with_drl(test.net, weights = E(test.net)$weight)
  
  # Select the boundary of network graph
  xmin <- min(test.Layout.drl[,1])
  xmax <- max(test.Layout.drl[,1])
  ymin <- min(test.Layout.drl[,2])
  ymax <- max(test.Layout.drl[,2])
  
  # Compute node degrees (number of links) and use that to set node size:
  arrivals.sum <- ((exp(V(test.net)$larrivals.sender)-1)+(exp(V(test.net)$larrivals.receiver-1)))
  V(test.net)$larrivals.total <- log1p((arrivals.sum))
  V(test.net)$size <- ((V(test.net)$larrivals.total)^2)*node_size
  
  # Set edge width based on weight:
  E(test.net)$width <- E(test.net)$larrivals*edge_width
  
  V(test.net)$label.color <- "black"
  V(test.net)$label <- V(test.net)$name
  V(test.net)$label.cex <- label_size
  
  message("Opening Telecoupling System...")
  WC <- arc.open(input_telecoupling_system)
  str_lst <- paste0("'", paste(df$ISO_3_CODE, collapse="', '"), "'")
  WC_df <- arc.select(WC, where_clause = paste0('ISO_3_CODE IN (', str_lst, ')'))

  WC_sp_df <- arc.shape2sp(arc.shape(WC_df))
  shape_info <- list(type="Polygon", WKT=arc.shapeinfo(arc.shape(WC_df))$WKT)
  
  WC_df_join <- inner_join(WC_df, df, by = 'ISO_3_CODE')
  
  message("Creating Output Shapefile...")
  SPDF = SpatialPolygonsDataFrame(WC_sp_df, data=WC_df_join)
  
  message("Creating Plots for Clusters...")
  result = tryCatch({
    pdf(out_pdf)
    
    plot(x=MyClusters.community, y=test.net, layout=test.Layout.drl, 
         mark.groups=NULL, edge.color = c("tomato2", "darkgrey")[crossing(MyClusters.community, test.net)+1],
         edge.arrow.size=0, rescale=F, xlim=c(xmin,xmax),ylim=c(ymin,ymax), asp=0, col = MyClusters.col)
    
    arc.write(path=out_fc, data=SPDF, shape_info=shape_info)
    
  }, finally = {
    dev.off()
  }
  )
  return(out_params)
}


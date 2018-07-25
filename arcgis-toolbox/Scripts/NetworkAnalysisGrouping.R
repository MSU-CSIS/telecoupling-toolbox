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
  nodes_table <- in_params[[1]]
  nodes_table_join <- in_params[[2]]
  link_table <- in_params[[3]]
  in_telecoupling_layer <- in_params[[4]]
  in_telecoupling_layer_join <- in_params[[5]]
  clustering_algorithm <- in_params[[6]]
  weight_within <- in_params[[7]]
  weight_between <- in_params[[8]]
  color_set <- in_params[[9]]
  node_size <- in_params[[10]]
  edge_width <- in_params[[11]]
  label_size <- in_params[[12]]
    
  #### Set output parameters ####
  out_pdf <- out_params[[1]]
  out_fc <- out_params[[2]]
  out_csv <- out_params[[3]]
  
  # To control thinkness/distances between nodes 
  edge.weights <- function(community, network, weight.within = weight_within, weight.between = weight_between) 
  {
    bridges <- crossing(communities = community, graph = network)
    weights <- ifelse(test = bridges, yes = weight.between, no = weight.within)
    return(weights) 
  }
  
  #### Model Input ####
  nodes_df <- read.csv(file=nodes_table, header=T, stringsAsFactors=FALSE, check.names=FALSE)
  links_df <- read.csv(file=link_table, header=T, stringsAsFactors=FALSE, check.names=FALSE)
  
  #USE THESE TWO LINES ONLY WHEN YOU RUN THE SCRIPT IN ARCGIS
  env <- arc.env()
  wkspath <- env$workspace	
  
  # change data frame format to igraph format
  network_graph <- graph_from_data_frame(d=links_df, vertices=nodes_df, directed=T)
  
  # create clusters
  message("Creating Clusters...")
  if (clustering_algorithm=="walktrap")
  {
    MyClusters.community <- cluster_walktrap(network_graph)
    community_df <- data.frame(V1 = unique(MyClusters.community)[[4]], cluster_N = as.numeric(unique(MyClusters.community)[[3]]))
    colnames(community_df)[1] <- nodes_table_join
  }
  
  if (clustering_algorithm == "spin_glass"){
    MyClusters.community <- cluster_spinglass(network_graph)
    community_df <- data.frame(V1 = unique(MyClusters.community)[[7]], cluster_N = as.numeric(unique(MyClusters.community)[[1]]))
	colnames(community_df)[1] <- nodes_table_join
  }
  
  community_df[ , which(names(community_df) == nodes_table_join)] <- as.character(community_df[ , which(names(community_df) == nodes_table_join)])
  
  # assign colors to clusters
  NumberOfColors <- length(unique(MyClusters.community))
  Colors <- brewer.pal(NumberOfColors, color_set)
  MyClusters.col <- Colors[membership(MyClusters.community)] 
  
  # change distances among nodes (within the same clusters & between clusters)
  E(network_graph)$weight <- edge.weights(MyClusters.community, network_graph)
  test.Layout.drl <- layout_with_drl(network_graph, weights = E(network_graph)$weight)
  
  # Select the boundary of network graph
  xmin <- min(test.Layout.drl[,1])
  xmax <- max(test.Layout.drl[,1])
  ymin <- min(test.Layout.drl[,2])
  ymax <- max(test.Layout.drl[,2])
  
  # Compute node degrees (number of links) and use that to set node size:
  arrivals.sum <- ((exp(V(network_graph)$larrivals.sender)-1)+(exp(V(network_graph)$larrivals.receiver-1)))
  V(network_graph)$larrivals.total <- log1p((arrivals.sum))
  V(network_graph)$size <- ((V(network_graph)$larrivals.total)^2)*node_size
  
  # Set edge width based on weight:
  E(network_graph)$width <- E(network_graph)$larrivals*edge_width
  
  V(network_graph)$label.color <- "black"
  V(network_graph)$label <- V(network_graph)$name
  V(network_graph)$label.cex <- label_size
  
  message("Reading Telecoupling Systems Layer...")
  tc_systems_arc_dataset <- arc.open(in_telecoupling_layer)
  str_lst <- paste0("'", paste(community_df[ , which(names(community_df) == nodes_table_join)], collapse="', '"), "'")
  #tc_systems_df <- arc.select(tc_systems_arc_dataset, where_clause = paste0('ISO_3_CODE IN (', str_lst, ')'))
  tc_systems_df <- arc.select(tc_systems_arc_dataset, where_clause = paste0(in_telecoupling_layer_join, " IN (", str_lst, ")"))

  message("Joining Network Table to Telecoupling Systems Layer...")
  tc_systems_df_join <- inner_join(tc_systems_df, community_df, by = setNames(nm=in_telecoupling_layer_join, nodes_table_join))
  #tc_systems_df_join <- merge(tc_systems_df, community_df, by.x = in_telecoupling_layer_join, by.y = nodes_table_join)
	
  tc_systems_spdf <- arc.shape2sp(arc.shape(tc_systems_df))

  message("Creating Output Shapefile...")
  SPDF = SpatialPolygonsDataFrame(tc_systems_spdf, data=tc_systems_df_join)
  shape_info <- list(type="Polygon", WKT=arc.shapeinfo(arc.shape(tc_systems_df))$WKT)

  message("Creating Output CSV file...")
  deg_stat = degree(network_graph)
  clo_stat = closeness(network_graph,normalized = TRUE)
  betw_stat = betweenness(network_graph)
  cen_stat = eigen_centrality(network_graph)$vector
  inte_csv = data.frame(degree = deg_stat,closeness = clo_stat,betweenness = betw_stat,centrality = cen_stat)
  print("Network Analysis Report:", quote = FALSE)
  print(inte_csv)

  message("Creating Plots for Clusters...")
  result = tryCatch({
    pdf(out_pdf)
    
    suppressWarnings(plot(x=MyClusters.community, y=network_graph, layout=test.Layout.drl, 
                          mark.groups=NULL, edge.color = c("tomato2", "darkgrey")[crossing(MyClusters.community, network_graph)+1],
                          edge.arrow.size=0, rescale=F, xlim=c(xmin,xmax),ylim=c(ymin,ymax), asp=0, col = MyClusters.col))
    
    #arc.write(path=out_fc, data=SPDF, shape_info=shape_info)
    
  }, finally = {
    dev.off()
  }
  )
  arc.write(path=out_fc, data=SPDF, shape_info=shape_info)
  write.csv(inte_csv,file = out_csv)
  return(out_params)
}


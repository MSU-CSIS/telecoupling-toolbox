library(igraph)
library(RColorBrewer)
library(dplyr)
library(sp)
#library(missMDA)

# To control thinkness/distances between nodes 
edge.weights <- function(community, network, weight.within = 100, weight.between = 2) 
{
	bridges <- crossing(communities = community, graph = network)
	weights <- ifelse(test = bridges, yes = weight.between, no = weight.within)
	return(weights) 
}

#needs to rename: test for ??? and WC for more generic usage

tool_exec <- function(in_params, out_params)
{
	#Load library
	if (!requireNamespace("igraph", quietly = TRUE))
    	install.packages("igraph")
  if (!requireNamespace("RColorBrewer", quietly = TRUE))
    	install.packages("RColorBrewer")
  if (!requireNamespace("dplyr", quietly = TRUE))
    	install.packages("dplyr")
	if (!requireNamespace("sp", quietly = TRUE))
    	install.packages("sp")

  require(igraph)
  #require(missMDA)
	require(dplyr)
	require(sp)
  require(RColorBrewer)
	
	#Get input parameters
	message("Reading Input Parameters...")
	input_nodes_table <- in_params[[1]]
	input_link_table <- in_params[[2]]
	input_telecoupling_system <- in_params[[3]]
	clustering_algorithm <- in_params[[4]]
	
	#Set output parameters
	out_pdf <- out_params[[1]]
	out_telecoupling_system <- out_params[[2]]

	# Input: nodes.csv for attributes of nodes; link.csv for attributes of edges 
	test.node <- read.csv(file=input_nodes_table, header=T, stringsAsFactors=FALSE, check.names=FALSE)
	test.link <- read.csv(file=input_link_table, header=T, stringsAsFactors=FALSE, check.names=FALSE)
	
	##USE THESE TWO LINES ONLY WHEN YOU RUN THE SCRIPT IN ARCGIS
	env <- arc.env()
	wkspath <- env$workspace	

	# change data frame format to igraph format
	test.net <- graph_from_data_frame(d=test.link, vertices=test.node, directed=T)

	# create clusters
	if (clustering_algorithm=="walktrap")
	{
		MyClusters.community <- cluster_walktrap(test.net)
	}

	if (clustering_algorithm=="label_propagation")
	{
		MyClusters.community <- cluster_label_prop(test.net)
	}

	df <- data.frame(ISO_3_CODE = unique(MyClusters.community)[[4]], cluster_N = as.numeric(unique(MyClusters.community)[[3]]))
	df$ISO_3_CODE <- as.character(df$ISO_3_CODE)

	# assign colors to clusters
	NumberOfColors <- length(unique(MyClusters.community))
	Colors <- brewer.pal(NumberOfColors, "Set3")
	MyClusters.col <- Colors[membership(MyClusters.community)] 

	# change distances among nodes (within the same clusters & between clusters)
	# BY Ming: Since it is hard to set distances among nodes in R (to show clusters), I used some wired steps as following: using both 'layout_with_drl" and 'layout_with_fr several times
	E(test.net)$weight <- edge.weights(MyClusters.community, test.net, weight.within=10)
	test.Layout.drl <- layout_with_drl(test.net, weights = E(test.net)$weight)

	E(test.net)$weight <- edge.weights(MyClusters.community, test.net, weight.within=20)
	test.Layout.drl <- layout_with_drl(test.net, use.seed=T, seed=test.Layout.drl, weights = E(test.net)$weight)

	E(test.net)$weight2 <- edge.weights(MyClusters.community, test.net, weight.within=10000)
	test.Layout <- layout_with_fr(test.net, coords= test.Layout.drl, weights = E(test.net)$weight2, start.temp=0.05, niter=10)

	# Select the boundary of network graph
	 xmin <- min(test.Layout[,1])
	 xmax <- max(test.Layout[,1])
	 ymin <- min(test.Layout[,2])
	 ymax <- max(test.Layout[,2])

	# Compute node degrees (number of links) and use that to set node size:
	arrivals.sum <- ((exp(V(test.net)$larrivals.sender)-1)+(exp(V(test.net)$larrivals.receiver-1)))
	V(test.net)$larrivals.total <- log1p((arrivals.sum))
	V(test.net)$size <- ((V(test.net)$larrivals.total)^2)*0.05
	
	# Set edge width based on weight:
	E(test.net)$width <- E(test.net)$larrivals*0.08

	V(test.net)$label.color <- "black"
	V(test.net)$label <- V(test.net)$name
	V(test.net)$label.cex <- 0.8

	# Plot
	g <- plot(x=MyClusters.community, y=test.net, layout=test.Layout, mark.groups=NULL, edge.color = c("tomato2", "darkgrey")[crossing(MyClusters.community, test.net)+1], edge.arrow.size=0, rescale=F, xlim=c(xmin,xmax),ylim=c(ymin,ymax), asp=0, col = MyClusters.col)
	## legend('topright', unique(MyClusters.community), lty=1, col=brewer.pal(NumberOfColors, "Set3"), bty='n', cex=.75)

	message("Opening system")
	WC <- arc.open(input_telecoupling_system)
	str_lst <- paste0("'", paste(df$ISO_3_CODE, collapse="', '"), "'")
	WC_df <- arc.select(WC, where_clause = paste0('ISO_3_CODE IN (', str_lst, ')'))

	WC_sp_df <- arc.shape2sp(arc.shape(WC_df))

	shape_info <- list(type="Polygon", WKT=arc.shapeinfo(arc.shape(WC_df))$WKT)

	WC_df_join <- inner_join(WC_df, df, by = 'ISO_3_CODE') 
	#WC_df_join <- left_join(WC_df, df, by = 'ISO_3_CODE') 
	#WC_df_join$cluster_N[is.na(WC_df_join$cluster_N)] <- ""

	SPDF = SpatialPolygonsDataFrame(WC_sp_df, data=WC_df_join)

	pdf(out_pdf)
	out_telecoupling_system <- arc.write(path="wkspath/network_output.shp", data=SPDF, shape_info=shape_info)
	
	dev.off()
	return(out_params)
}


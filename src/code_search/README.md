# Instructions for Using Code Search

The scripts in this repository can be used for various tasks, including creating an Elasticsearch database, searching the database, training a Graph Neural Network (GNN), generating graph representations of Python code, and more. To apply these tools to your own code, follow the steps below:

1. **Generate Graph Representations:**
   - Navigate to the `graph_gen` directory.
   - Follow the instructions in the `README` file to convert a GitHub repository into graphical representations of the code.

2. **Build the Elasticsearch Database:**
   - Run `main.py` with the `--build --only-database` argument.
   - This will create the Elasticsearch database without training a new model. 
   - A pre-trained model for `bi_ggnn` is available in the `output` directory and is recommended for use.

3. **Search the Database:**
   - After the database is built, use the `search` argument with `main.py` to perform searches.
   - You can use natural language queries to find relevant functions.

This app was made to run in browser. It utilizes the Plotly Dash framework to help users make more informed investment decisions.

What this app does:
  -user will feed the input as many stock symbols as they want, press enter when you're done
  -the app with calculate 1000 portfolios of varying percentages of given stocks and calculate
   statistics like expected return, volatility, skew and kurtosis
  -the app will plot all 4 moments on a 3D coordinate axis and display the information in a data
   table
  -you can use the illustration and filter criteria in the data table to pick a combination of 
   stocks that suits your needs! Have fun investing!

What this app isn't:
  -a stock tracker
  -a stock recommender
  -a brokerage
  
Troubleshooting:
  -if you run this in an IDE that isn't JupyterLab then you should consider importing
   plotly Dash instead of JupyterDash
  -since your laptop acts as a server, you might get this thing called a "Port Error:"
   which means it's already hosting the web app in a location and can't overwrite it,
   to fix it try changing the port number where it says app.run_server...
   
Future iterations:
  -it would be cool to host this online eventually
  -ideally the user would be able to interact entirely with the front end of the app
   so hopefully I can figure that out
  -I need to figure out how Plotly Dash stores memory so I can build the table and graph
   in the background, that way the user doesn't have to worry about the code part

If you like to invest and are familiar with python and Plotly Dash, let's colaborate!

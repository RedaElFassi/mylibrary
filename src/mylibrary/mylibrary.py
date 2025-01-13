from pybacktestchain.data_module import FirstTwoMoments
from pybacktestchain.broker import Backtest, StopLoss
from pybacktestchain.blockchain import load_blockchain
from datetime import datetime
import pandas as pd
from io import StringIO

# Set verbosity for logging
verbose = False  # Set to True to enable logging, or False to suppress it

backtest = Backtest(
    initial_date=datetime(2019, 1, 1),
    final_date=datetime(2020, 1, 1),
    information_class=FirstTwoMoments,
    risk_model=StopLoss,
    name_blockchain='backtest',
    verbose=verbose
)

backtest.run_backtest()

block_chain = load_blockchain('backtest')
print(str(block_chain))
# check if the blockchain is valid
print(block_chain.is_valid())




for block in block_chain.chain:
    if block.name_backtest == "Genesis Block":  # Ignorer le bloc Genesis
        continue
    
    print(f"Processing block: {block.name_backtest}")
    
    try:
        # Convertir les données en DataFrame
        df = pd.read_csv(StringIO(block.data), delim_whitespace=True)
        print("Data as DataFrame:")
        print(df.head())
    except Exception as e:
        print(f"Error converting block data to DataFrame: {e}")
    print("-" * 80)

print(df)




import plotly.express as px
from dash import Dash, dcc, html, Input, Output

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px

# Charger les données dans un DataFrame (vous avez déjà df, donc on l'utilise directement)
# df = ... (votre dataframe ici)

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf

def compute_pnl(df):
    df['Average_Buy_Price'] = df.groupby('Ticker', group_keys=False)['Price'].transform(
        lambda x: x.expanding().mean()
    )
    df['Transaction_PnL'] = np.where(
        df['Action'] == 'SELL',
        (df['Price'] - df['Average_Buy_Price']) * df['Quantity'],
        0
    )
    df['Cumulative_PnL'] = df.groupby('Date')['Transaction_PnL'].cumsum()
    overall_pnl = df.groupby('Date')['Cumulative_PnL'].sum().reset_index(name='Overall_PnL')
    stock_pnl = df.groupby(['Date', 'Ticker'])['Cumulative_PnL'].sum().reset_index()
    return overall_pnl, stock_pnl


def compute_returns(df):
    df['Average_Buy_Price'] = df.groupby('Ticker', group_keys=False)['Price'].transform(
        lambda x: x.expanding().mean()
    )
    df['Stock_Value'] = df['Quantity'] * df['Price']
    df['Portfolio_Value'] = df['Cash'] + df.groupby('Date', group_keys=False)['Stock_Value'].transform('sum')
    df['Daily_Return'] = df['Portfolio_Value'].pct_change().fillna(0)

    portfolio_returns = df[['Date', 'Daily_Return']].drop_duplicates()
    stock_returns = df[['Date', 'Ticker', 'Daily_Return']].drop_duplicates()

    portfolio_sharpe = sharpe_ratio(portfolio_returns['Daily_Return'])
    stock_sharpes = df.groupby('Ticker')['Daily_Return'].apply(sharpe_ratio).reset_index()
    stock_sharpes.columns = ['Ticker', 'Sharpe_Ratio']

    return portfolio_returns, stock_returns, portfolio_sharpe, stock_sharpes


def sharpe_ratio(returns, risk_free_rate=0.01):
    excess_returns = returns - risk_free_rate / 252
    mean_excess_return = excess_returns.mean()
    std_excess_return = excess_returns.std()
    if std_excess_return == 0:
        return 0
    return mean_excess_return / std_excess_return


from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

def fetch_and_compute_indicators(tickers):
    """
    Fetch historical data and compute moving averages and Bollinger Bands for a list of tickers.
    Handles NaN values generated by rolling calculations.
    """
    # Define the date range
    today = datetime.today()
    end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday's date
    start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year ago from today

    # Initialize a list to store processed DataFrames
    processed_data = []

    for ticker in tickers:
        try:
            # Fetch historical data using Ticker object and history() method
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, auto_adjust=False, actions=False)

            # If data is empty, log and skip
            if data.empty:
                print(f"No data available for {ticker}")
                continue

            # Reset index to have a clean DataFrame
            data = data.reset_index()

            # Compute moving averages
            data['MA_15'] = data['Close'].rolling(window=15).mean()
            data['MA_30'] = data['Close'].rolling(window=30).mean()
            data['MA_45'] = data['Close'].rolling(window=45).mean()

            # Compute Bollinger Bands
            data['BB_Mid'] = data['Close'].rolling(window=20).mean()
            data['BB_Std'] = data['Close'].rolling(window=20).std()  # Rolling standard deviation
            data['BB_Upper'] = data['BB_Mid'] + 2 * data['BB_Std']  # Upper Band
            data['BB_Lower'] = data['BB_Mid'] - 2 * data['BB_Std']  # Lower Band

            # Add Ticker column for identification
            data['Ticker'] = ticker

            # Option 1: Drop rows with NaN values (useful if analysis doesn't require them)
            data.dropna(inplace=True)

            # OR Option 2: Fill NaN values with appropriate values (e.g., forward fill or 0)
            # Uncomment one of the following lines if you'd rather fill NaNs:
            # data.fillna(method='ffill', inplace=True)  # Forward-fill NaN values
            # data.fillna(0, inplace=True)  # Replace NaNs with 0

            # Drop temporary columns used for computation (if not needed)
            data.drop(columns=['BB_Std'], inplace=True)

            # Append processed data to the list
            processed_data.append(data)

        except Exception as e:
            # Log any error that occurs during processing
            print(f"Error processing {ticker}: {e}")

    # Combine all processed data into a single DataFrame
    if processed_data:
        return pd.concat(processed_data, ignore_index=True)
    else:
        # Return an empty DataFrame if no data was processed
        return pd.DataFrame()





print(fetch_and_compute_indicators('AAPL'))

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='stock-selector',
                options=[{'label': ticker, 'value': ticker} for ticker in df['Ticker'].unique()],
                value=df['Ticker'].unique(),
                multi=True,
                placeholder="Select stocks to display"
            )
        ], width=12)
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='overall-pnl-chart', config={'displayModeBar': False})
        ], width=6),
        dbc.Col([
            dcc.Graph(id='stock-pnl-chart', config={'displayModeBar': False})
        ], width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='returns-chart', config={'displayModeBar': False})
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Sharpe Ratios", className="text-center"),
            html.Table(id='sharpe-ratio-table', className="table table-striped table-bordered")
        ], width=12)
    ], className="mb-4"),

    html.Hr(),  # Line to distinguish sections
    html.H3("Statistical Indicators on Past Year Data", className="text-center mt-4 mb-4"),

    dbc.Row(id='dynamic-indicator-graphs', className="gy-4")  # Classe pour espacement vertical
], fluid=True)


# Callbacks
@app.callback(
    Output('overall-pnl-chart', 'figure'),
    Input('stock-selector', 'value')
)
def update_pnl_chart(selected_stocks):
    filtered_df = df[df['Ticker'].isin(selected_stocks)]
    overall_pnl, _ = compute_pnl(filtered_df)
    fig = px.line(
        overall_pnl,
        x='Date',
        y='Overall_PnL',
        title="Overall Portfolio PnL Over Time",
        labels={'Overall_PnL': 'PnL', 'Date': 'Date'}
    )
    return fig


@app.callback(
    Output('stock-pnl-chart', 'figure'),
    Input('stock-selector', 'value')
)
def update_stock_pnl_chart(selected_stocks):
    filtered_df = df[df['Ticker'].isin(selected_stocks)]
    _, stock_pnl = compute_pnl(filtered_df)
    fig = px.line(
        stock_pnl,
        x='Date',
        y='Cumulative_PnL',
        color='Ticker',
        title="Stock PnL Over Time",
        labels={'Cumulative_PnL': 'PnL', 'Ticker': 'Stock'}
    )
    return fig


@app.callback(
    Output('returns-chart', 'figure'),
    Input('stock-selector', 'value')
)
def update_returns_chart(selected_stocks):
    filtered_df = df[df['Ticker'].isin(selected_stocks)]
    _, stock_returns, _, _ = compute_returns(filtered_df)
    fig = px.line(
        stock_returns,
        x='Date',
        y='Daily_Return',
        color='Ticker',
        title="Daily Returns by Stock",
        labels={'Daily_Return': 'Daily Return', 'Date': 'Date'}
    )
    return fig


@app.callback(
    Output('sharpe-ratio-table', 'children'),
    Input('stock-selector', 'value')
)
def update_sharpe_ratios(selected_stocks):
    filtered_df = df[df['Ticker'].isin(selected_stocks)]
    _, _, portfolio_sharpe, stock_sharpes = compute_returns(filtered_df)
    table_header = [
        html.Thead(html.Tr([html.Th("Ticker"), html.Th("Sharpe Ratio")]))
    ]
    table_body = [
        html.Tr([html.Td("Portfolio"), html.Td(f"{portfolio_sharpe:.2f}")])
    ]
    for _, row in stock_sharpes.iterrows():
        table_body.append(html.Tr([html.Td(row['Ticker']), html.Td(f"{row['Sharpe_Ratio']:.2f}")]))
    return table_header + [html.Tbody(table_body)]


# Callback pour mettre à jour les graphiques dynamiques
@app.callback(
    Output('dynamic-indicator-graphs', 'children'),
    Input('stock-selector', 'value')  # La valeur sélectionnée dans la liste déroulante
)
def update_dynamic_graphs(selected_stocks):
    if not selected_stocks:
        return [html.Div("No stocks selected.", style={'textAlign': 'center', 'padding': '20px'})]

    graphs = []
    for ticker in selected_stocks:
        stock_data = fetch_and_compute_indicators([ticker])

        if stock_data.empty:
            graphs.append(html.Div(f"No data available for {ticker}.", style={'textAlign': 'center', 'padding': '10px'}))
            continue

        # Crée un graphique pour chaque action
        fig = px.line(stock_data, x='Date', y='Close', title=f"{ticker} - Statistical Indicators")
        fig.add_scatter(x=stock_data['Date'], y=stock_data['MA_15'], mode='lines', name='MA 15')
        fig.add_scatter(x=stock_data['Date'], y=stock_data['MA_30'], mode='lines', name='MA 30')
        fig.add_scatter(x=stock_data['Date'], y=stock_data['MA_45'], mode='lines', name='MA 45')
        fig.add_scatter(
            x=stock_data['Date'], y=stock_data['BB_Upper'],
            mode='lines', line=dict(width=0), name='Upper Band',
            showlegend=False
        )
        fig.add_scatter(
            x=stock_data['Date'], y=stock_data['BB_Lower'],
            mode='lines', line=dict(width=0), name='Lower Band',
            fill='tonexty', fillcolor='rgba(173,216,230,0.3)',  # Couleur bleu clair
            showlegend=False
        )

        graphs.append(
            dbc.Col([
                dcc.Graph(
                    id=f"{ticker}-indicator-chart",
                    figure=fig,
                    config={'displayModeBar': False}
                )
            ], width=6)  # Chaque graphique occupe la moitié de la ligne
        )

    return graphs





import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    #app.run_server(debug=False, port=8050)
    app.run_server(host='0.0.0.0', port=8050, debug=True)
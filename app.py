# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from backtester import Backtester
import utils
from strategies import sma_crossover, rsi_meanrev, market_mood

# Page configuration
st.set_page_config(
    page_title="Quant Trading Gym",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem;
    }
    .strategy-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📈 Quant Trading Gym</h1>', unsafe_allow_html=True)

# Sidebar for user inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Date range
    st.subheader("Date Range")
    start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
    end_date = st.date_input("End Date", pd.to_datetime("2024-01-01"))
    
    # Initial capital
    initial_capital = st.number_input("Initial Capital ($)", value=100000, min_value=1000, step=1000)
    
    # Commission
    commission = st.number_input("Commission (%)", value=0.0, min_value=0.0, max_value=5.0, step=0.01)
    
    st.header("🎯 Strategy Selection")
    selected_strategies = st.multiselect(
        "Choose strategies to run:",
        ["SMA Crossover", "RSI Mean Reversion", "Market Mood Detector"],
        default=["SMA Crossover", "RSI Mean Reversion"]
    )
    
    # Strategy-specific parameters
    st.header("📊 Strategy Parameters")
    
    if "SMA Crossover" in selected_strategies:
        st.subheader("SMA Crossover")
        sma_short = st.slider("Short SMA Period", 5, 50, 20, key="sma_short")
        sma_long = st.slider("Long SMA Period", 20, 200, 50, key="sma_long")
    
    if "RSI Mean Reversion" in selected_strategies:
        st.subheader("RSI Mean Reversion")
        rsi_period = st.slider("RSI Period", 5, 30, 14, key="rsi_period")
        rsi_oversold = st.slider("Oversold Level", 10, 50, 30, key="rsi_oversold")
        rsi_overbought = st.slider("Overbought Level", 50, 90, 70, key="rsi_overbought")
    
    if "Market Mood Detector" in selected_strategies:
        st.subheader("Market Mood Detector")
        mm_window = st.slider("Z-Score Window", 10, 100, 20, key="mm_window")
        mm_entry = st.slider("Entry Z-Score", 1.0, 3.0, 2.0, key="mm_entry")
        mm_exit = st.slider("Exit Z-Score", 0.1, 1.0, 0.5, key="mm_exit")
    
    # Asset selection
    st.header("📦 Asset Selection")
    asset_options = ["QQQ", "SPY", "BTC-USD", "ETH-USD", "AAPL", "GOOGL", "MSFT"]
    selected_asset = st.selectbox("Primary Asset", asset_options, index=0)
    
    if "Market Mood Detector" in selected_strategies:
        pair_asset = st.selectbox("Pair Asset (for Market Mood)", asset_options, index=2)

# Run strategies button
if st.sidebar.button("🚀 Run Backtest", type="primary"):
    results = {}
    metrics_data = {}
    
    # Create tabs for results
    tab1, tab2, tab3 = st.tabs(["📊 Performance", "📈 Equity Curves", "📋 Detailed Results"])
    
    with st.spinner("Running backtests..."):
        # Run selected strategies
        if "SMA Crossover" in selected_strategies:
            with st.expander("SMA Crossover Results", expanded=True):
                df = utils.download_data(selected_asset, start=start_date, end=end_date)
                price = df['close']
                
                # Generate signals with custom parameters
                def sma_strategy(p):
                    return sma_crossover.generate_signals(p, short_window=sma_short, long_window=sma_long)
                
                signals = sma_strategy(price)
                bt = Backtester(price, cash=initial_capital, commission=commission/100)
                equity = bt.run_signals(signals)
                results['SMA Crossover'] = equity
                metrics = Backtester.performance_metrics(equity)
                metrics_data['SMA Crossover'] = metrics
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Return", f"{metrics['total_return']:.2%}")
                with col2:
                    st.metric("Annual Return", f"{metrics['ann_return']:.2%}")
                with col3:
                    st.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
                with col4:
                    st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
                
                # Plot
                fig, ax = plt.subplots(figsize=(10, 4))
                equity.plot(ax=ax)
                ax.set_title("SMA Crossover Equity Curve")
                ax.set_ylabel("Equity ($)")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        if "RSI Mean Reversion" in selected_strategies:
            with st.expander("RSI Mean Reversion Results", expanded=True):
                df = utils.download_data(selected_asset, start=start_date, end=end_date)
                price = df['close']
                
                # Generate signals with custom parameters
                def rsi_strategy(p):
                    return rsi_meanrev.generate_signals(p, low=rsi_oversold, high=rsi_overbought, period=rsi_period)
                
                signals = rsi_strategy(price)
                bt = Backtester(price, cash=initial_capital, commission=commission/100)
                equity = bt.run_signals(signals)
                results['RSI Mean Reversion'] = equity
                metrics = Backtester.performance_metrics(equity)
                metrics_data['RSI Mean Reversion'] = metrics
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Return", f"{metrics['total_return']:.2%}")
                with col2:
                    st.metric("Annual Return", f"{metrics['ann_return']:.2%}")
                with col3:
                    st.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
                with col4:
                    st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
                
                # Plot
                fig, ax = plt.subplots(figsize=(10, 4))
                equity.plot(ax=ax)
                ax.set_title("RSI Mean Reversion Equity Curve")
                ax.set_ylabel("Equity ($)")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        if "Market Mood Detector" in selected_strategies:
            with st.expander("Market Mood Detector Results", expanded=True):
                a = utils.download_data(selected_asset, start=start_date, end=end_date)
                b = utils.download_data(pair_asset, start=start_date, end=end_date)
                price_a = a['close']
                price_b = b['close']
                
                # Generate signals with custom parameters
                dfpos = market_mood.generate_pairs_signals(price_a, price_b, window=mm_window, entry_z=mm_entry, exit_z=mm_exit)
                
                # Calculate equity
                notional = initial_capital / 2
                eq_a = (notional * (price_a.reindex(dfpos.index) / price_a.reindex(dfpos.index).iloc[0]) * dfpos['pos_a'])
                eq_b = (notional * (price_b.reindex(dfpos.index) / price_b.reindex(dfpos.index).iloc[0]) * dfpos['pos_b'])
                combined = eq_a.fillna(0) + eq_b.fillna(0)
                combined.index = dfpos.index
                results['Market Mood Detector'] = combined
                metrics = Backtester.performance_metrics(combined)
                metrics_data['Market Mood Detector'] = metrics
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Return", f"{metrics['total_return']:.2%}")
                with col2:
                    st.metric("Annual Return", f"{metrics['ann_return']:.2%}")
                with col3:
                    st.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
                with col4:
                    st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
                
                # Plot
                fig, ax = plt.subplots(figsize=(10, 4))
                combined.plot(ax=ax)
                ax.set_title("Market Mood Detector Equity Curve")
                ax.set_ylabel("Equity ($)")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        # Comparison tab
        with tab1:
            st.header("Strategy Comparison")
            
            if len(results) > 1:
                # Normalized comparison
                fig, ax = plt.subplots(figsize=(12, 6))
                for name, equity in results.items():
                    normalized = equity / equity.iloc[0]
                    normalized.plot(ax=ax, label=name, linewidth=2)
                
                ax.legend()
                ax.set_title("Normalized Equity Curve Comparison")
                ax.set_ylabel("Normalized Equity")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
            
            # Metrics comparison table
            st.subheader("Performance Metrics Comparison")
            metrics_df = pd.DataFrame(metrics_data).T
            st.dataframe(metrics_df.style.format({
                'total_return': '{:.2%}',
                'ann_return': '{:.2%}', 
                'ann_vol': '{:.2%}',
                'max_drawdown': '{:.2%}',
                'sharpe': '{:.2f}'
            }))
        
        with tab2:
            st.header("Individual Equity Curves")
            for name, equity in results.items():
                fig, ax = plt.subplots(figsize=(10, 4))
                equity.plot(ax=ax)
                ax.set_title(f"{name} Equity Curve")
                ax.set_ylabel("Equity ($)")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        with tab3:
            st.header("Detailed Results")
            for name, metrics in metrics_data.items():
                st.subheader(name)
                st.json(metrics)

else:
    # Welcome screen
    st.info("👈 Configure your backtest in the sidebar and click 'Run Backtest' to get started!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 SMA Crossover")
        st.write("Uses moving average crossovers to generate buy/sell signals")
        st.code("""
        Buy: Short MA > Long MA
        Sell: Short MA < Long MA
        """)
    
    with col2:
        st.subheader("📈 RSI Mean Reversion")
        st.write("Trades based on overbought/oversold RSI levels")
        st.code("""
        Buy: RSI < Oversold level
        Sell: RSI > Overbought level  
        """)
    
    with col3:
        st.subheader("🌐 Market Mood Detector")
        st.write("Pairs trading strategy based on statistical arbitrage")
        st.code("""
        Long spread: Z-score < -Entry
        Short spread: Z-score > Entry
        Exit: |Z-score| < Exit
        """)

# Footer
st.markdown("---")
st.caption("Quant Trading Gym - Interactive Backtesting Platform")
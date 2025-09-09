# -- SERVER SIDE (Yahoo Finance MCP Server) --

# ---------------- Imports ---------------- #
import yfinance as yf  # For stock market data
from typing import Dict, Any, Optional  # Type hints
from pydantic import BaseModel  # Data validation with Pydantic
from datetime import datetime  # For timestamps

from mcp.server.fastmcp import FastMCP, Context  # MCP server utilities

# ---------------- Initialize MCP Server ---------------- #
# Create an MCP server instance with a descriptive name
mcp = FastMCP("Yahoo Finance API")

# ---------------- Data Model ---------------- #
# Pydantic model to validate and structure filter inputs
class SectorFilter(BaseModel):
    sector: Optional[str] = None  # Optional argument, e.g., "Technology"

# ---------------- Tool 1: Get Current Price ---------------- #
@mcp.tool()
def get_current_price(ticker: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Fetch the current (latest closing) price of a stock.

    Args:
        ticker: Stock symbol (e.g., AAPL, MSFT)
    """
    # Log request to server console (if context is provided)
    if ctx:
        ctx.info(f"Fetching current price for {ticker}")

    try:
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period="1d")  # Get 1-day history

        if hist.empty:
            return {"error": "No data available"}

        # Last closing price = "current" price
        price = hist['Close'].iloc[-1]
        return {
            "symbol": ticker,
            "price": round(price, 2),
            "currency": "USD",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Handle errors gracefully
        return {"error": str(e)}

# ---------------- Tool 2: Get Company Info ---------------- #
@mcp.tool()
def get_company_info(ticker: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Get detailed company information.

    Args:
        ticker: Stock symbol (e.g., AAPL, MSFT)
    """
    if ctx:
        ctx.info(f"Fetching company information for {ticker}")

    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info  # Dictionary of metadata about the company

        # Extract key fields
        relevant_info = {
            "symbol": ticker,
            "name": info.get("shortName", "Unknown"),
            "longName": info.get("longName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "website": info.get("website", "Unknown"),
            "marketCap": info.get("marketCap"),
            "forwardPE": info.get("forwardPE"),
            "dividendYield": info.get("dividendYield"),
            "trailingEps": info.get("trailingEps"),
            "description": info.get("longBusinessSummary", "No description available"),
        }
        return relevant_info
    except Exception as e:
        return {"error": str(e)}

# ---------------- Tool 3: List Popular Tickers ---------------- #
@mcp.tool()
def list_popular_tickers(filter: SectorFilter = SectorFilter()) -> Dict[str, Any]:
    """
    List popular stock tickers, optionally filtered by sector.

    Args:
        filter: SectorFilter with optional sector name
                (Technology, Consumer, Financial, Healthcare, Energy)
    """
    # Hardcoded popular tickers (for demo purposes)
    popular_tickers = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
        "Consumer": ["AMZN", "WMT", "COST", "MCD", "NKE"],
        "Financial": ["JPM", "BAC", "V", "MA", "BRK-B"],
        "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    }

    sector = filter.sector  # Optional input

    if sector and sector in popular_tickers:
        # Return tickers for a specific sector
        return {
            "sector": sector,
            "tickers": [{"symbol": s, "uri": f"/tickers/{s}"} for s in popular_tickers[sector]]
        }
    elif sector:
        # Invalid sector input
        return {"error": f"Sector '{sector}' not found", "available_sectors": list(popular_tickers.keys())}
    else:
        # Return all tickers if no sector is specified
        return {
            sec: [{"symbol": s, "uri": f"/tickers/{s}"} for s in tks]
            for sec, tks in popular_tickers.items()
        }

# ---------------- Run MCP Server ---------------- #
# Standard Python pattern: run server only if script is executed directly
if __name__ == "__main__":
    # Transport = "stdio" → MCP communicates via standard input/output
    mcp.run(transport="stdio")

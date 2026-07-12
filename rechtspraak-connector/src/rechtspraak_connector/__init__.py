"""Rechtspraak API Connector for Gelre Advocaten.

Pulls case law (jurisprudentie) from the public Rechtspraak Open Data API,
filters it to the firm's practice areas, and exports it to Supabase and/or
Obsidian markdown — cleanly structured so a RAG/MCP agent can be built on top.
"""
__version__ = "0.1.0"

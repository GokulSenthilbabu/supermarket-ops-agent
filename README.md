@'
# Supermarket Ops Agent

A Telegram-based AI agent for running day-to-day operations of an Indian supermarket/kirana store.

## Overview

The Supermarket Ops Agent provides a conversational interface for inventory, products, billing, GST, payments, Khata credit, daily closing, and sales analytics.

Users interact with the system through Telegram. The AI agent orchestrates business tools instead of using a traditional regex/keyword intent router.

## Architecture

Telegram → Vercel Webhook → AI Agent → Business Tools → Supabase PostgreSQL

## Core Features

- Product creation and catalog management
- Inventory and stock receiving
- Stock-level checking
- Low-stock identification
- Draft bill creation and editing
- Bill finalization
- GST calculation
- Cash, UPI and Card payments
- Oversell protection
- Below-cost selling protection
- Khata credit ledger
- Customer payment recording
- Daily sales summary
- Daily close
- PDF invoice generation
- Weekly sales analysis
- PPTX analytics deck generation
- Persistent operational preferences
- `/new` conversation reset

## Agent Design

The system follows an agent-first orchestration approach.

The agent interprets the user's request and selects the appropriate business tool. Business rules are enforced inside the tools and database operations rather than relying on regex-based intent routing.

## Business Rules

### Inventory
Stock is increased through stock-in operations and decreased when finalized bills are completed.

### Billing
Bills support multiple products, quantities, edits and payment modes.

### GST
GST is calculated according to the product tax configuration and included correctly in invoice totals.

### Oversell Protection
A bill cannot be finalized when requested quantity exceeds available stock.

### Below-Cost Protection
The system prevents selling products below their configured cost price.

### Khata
Customer credit balances are maintained in a persistent ledger. Payments reduce outstanding balances.

## Persistence

The application uses Supabase PostgreSQL for persistent storage.

Main operational data includes:

- Products
- Inventory
- Bills
- Bill items
- Customers
- Khata transactions
- Preferences

## Generated Artifacts

The application generates:

- PDF invoices
- Weekly PPTX sales analysis
- Sales charts
- Product sales charts
- Payment distribution charts

## Deployment

### Telegram

Bot:

`@gokul_supermarket_ops_agent_bot`

### Backend

Deployed using Vercel.

Production domain:

`https://supermarket-ops-agent-chi.vercel.app`

### Database

Supabase PostgreSQL.

## Local Setup

Create and activate a Python virtual environment:

```bash
python -m venv .venv
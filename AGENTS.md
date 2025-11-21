# Agents.md – Hackathon System Overview



## Overview

This hackathon project is a multi-agent AI system that predicts the next fashion trend and generates AI-based clothing visuals. It uses **Postman MCP**, **Redis**, and **Sanity** in innovative ways to simulate parallel agent workflows, state caching, and live content publishing. Built in under 2 hours using FastAPI + hosted AI tools, the system is optimized for demo impact.

---

## 🧠 Agent Architecture

### 1. 🧵 Trend Agent (`/trend`)

* **Purpose**: Synthesizes a future clothing trend based on social buzz or sales keywords.

* **Input**: Text signals (hashtags, product trends).

* **Output**: `trend_name`, `trend_description`.

* **Backend**: Python (FastAPI), optional use of OpenAI or Claude to generate natural language trend descriptions.

### 2. 🖼️ Image Generation Agent (`/generate-images`)

* **Purpose**: Turns a trend description into visuals using open-source diffusion models.

* **Input**: `trend_description`, `num_images`

* **Output**: List of `image_urls`

* **Backend**: Async FastAPI with parallel `httpx` calls to hosted **FLUX.1** or **Stable Diffusion 3** (e.g., via Replicate, Fal).

### 3. 🤖 Orchestrator Agent (`/run-pipeline`)

* **Purpose**: Coordinates the full pipeline: checks Redis cache, calls trend + image agents in sequence.

* **Behavior**:

  * If Redis has a cached result: return it

  * Else:

    1. Call `/trend`

    2. Call `/generate-images` in parallel

    3. Publish results to **Sanity**

    4. Cache in Redis

* **Output**: Final payload with trend + images, ready for frontend or export

---

## 🗃️ Redis – Smart Coordination Layer

* **Purpose**: Speed and fault tolerance via caching.

* **Uses**:

  * Cache trend + image outputs (`pipeline:{hash}`) for 15–30 mins

  * Share intermediate state between agents

  * Avoid redundant API calls during multiple orchestrator runs

* **Bonus**: Trend data in Redis can be visualized or scored in a leaderboard (e.g., most popular trend of the day)

---

## 📡 Postman + MCP – API & Agent Control Layer

* **Postman Use**:

  * All agents (`/trend`, `/generate-images`, `/run-pipeline`) defined in a Postman Collection

  * Collection imported into MCP

* **MCP Use**:

  * Turns your endpoints into "tools" a Claude or GPT agent can control via natural language

  * AI can reason: "First I'll get a trend, then generate images, then publish"

  * **MVP Demo**: Live call to `/run-pipeline` from Claude via MCP

* **Why it's innovative**:

  * You orchestrate your **entire pipeline with an LLM and Postman**, without writing glue code

  * Makes your hackathon feel like AGI-powered orchestration

---

## 🗞️ Sanity – Headless CMS Output Layer

* **Purpose**: Persist & publish final trend results for live display or front-end consumption

* **Used for**:

  * Posting each trend as a new document (e.g., `trend_{date}`)

  * Includes `title`, `description`, and `image_urls`

  * Allows you to build a **fashion trend showcase site** or dashboard on top of Sanity

* **Bonus**:

  * You can use **GROQ** to query trends by tag, date, or keyword

  * Use Sanity webhooks to trigger email or Slack alerts when a new trend is published

---

## 🧪 Demo Tips for Hackathon

* Pre-load a few sample signals like:

  * Social: `#balletcore`, `#coquette`, `#retro90s`

  * Sales: "plaid skirts up 45%", "cropped puffer jackets"

* Hit `/run-pipeline` in Postman or via Claude (MCP)

* Show:

  * JSON output (trend + images)

  * Sanity Studio with newly published trend

  * Optional: embed the image URLs into a frontend like Vercel/Next.js

---

## ✨ Innovation Summary

| Component       | Innovative Use                                         |

| --------------- | ------------------------------------------------------ |

| **Postman MCP** | Agents exposed as LLM-callable tools for auto-pipeline |

| **Redis**       | Coordination + speed layer with TTL & shared state     |

| **Sanity**      | Trend publishing CMS for real-time AI content sharing  |

| **Parallelism** | Image generation is async (concurrent API calls)       |

---

## 🔚 Closing

You don't need a full LLM backend or scraped data to tell a strong story. This system fakes nothing — every agent works — and thanks to Postman + Sanity + Redis, your hackathon demo shows off AI agents that think, generate, and publish fashion intelligence in real time.


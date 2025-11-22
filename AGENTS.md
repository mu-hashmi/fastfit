## **Overview**

**FastFit Radar** is an agent-driven personalized clothing notification system that monitors brand new releases from RSS feeds, stores products in Redis Memory, learns user preferences from feedback, and sends personalized email notifications based on individual taste profiles.

Agents operate in a loop:  
 **Fetch RSS Feeds → Store Products in Redis Memory → Match Products to User Preferences → Send Personalized Notifications → Learn from Feedback.**

The goal is **personalization \+ speed**, not complexity.

---

## **Core Data Sources**

* **RSS Feeds (easiest for POC)**

  * Fashion brand RSS feeds (Adidas, HYPEBEAST, Luxury Daily, etc.)

  * Poll feeds every 5-10 minutes for new product releases

  * Extract: product name, description, brand, image URL, link, release date

---

## **Memory Layer (Redis/RedisVL via Agent Memory Server)**

Each product is stored as:

`{`  
  `"id": "string",`  
  `"text": "product name + description",`  
  `"brand": "string",`  
  `"image_url": "string",`  
  `"product_url": "string",`  
  `"embedding": [vector]`  
`}`

Each user preference is stored as:

`{`  
  `"user_id": "email",`  
  `"liked_product_ids": ["id1", "id2"],`  
  `"disliked_product_ids": ["id3"],`  
  `"preferred_brands": ["brand1", "brand2"],`  
  `"taste_profile_embedding": [vector],`  
  `"notification_frequency": "daily|weekly|realtime"`  
`}`

Vector search: Used for matching products to user taste profiles via semantic similarity.

Agents must write products to Redis **before** matching.

---

## **User Preference Learning**

Input: User feedback (good/bad clicks on email notifications)

Process:
1. Store liked/disliked product IDs
2. Extract embeddings from liked products
3. Build taste profile embedding (average of liked products)
4. Update preferred brands based on liked products
5. Use taste profile for future product matching

Output: Updated user preference profile in Redis Memory

---

## **Product Matching (Semantic Search)**

Input: New products + User taste profile

Process:
1. Retrieve user's taste profile embedding from Redis
2. Search for products similar to taste profile (semantic search)
3. Filter by preferred brands (if user has preferences)
4. Exclude already-disliked products
5. Rank by similarity score

Output: Array of matched products for user:

`{`  
  `"product_id": "string",`  
  `"name": "string",`  
  `"brand": "string",`  
  `"description": "string",`  
  `"image_url": "string",`  
  `"product_url": "string",`  
  `"similarity_score": number`  
`}`

---

## **Email Notification System**

For each user with matching products:

1. Generate personalized email with top 5-10 matched products
2. Include good/bad buttons for each product
3. Track email opens and clicks
4. Update user preferences based on feedback

Email format:
- Subject: "New releases matching your style"
- Body: Product cards with images, links, good/bad buttons
- Footer: Unsubscribe link, preference settings link

---

## **Expected Agent Behaviors**

1. **Be deterministic** — follow JSON formats exactly.

2. **Be personalized** — only show products matching user taste profiles.

3. **Be efficient** — limit output size; avoid long prose.

4. **Be factual** — never fabricate products or brands.

5. **Be modular** — each step should be callable independently:

   * `fetch_rss_feeds`

   * `store_products_redis`

   * `get_user_preferences`

   * `match_products_to_user`

   * `send_notifications`

   * `update_preferences_from_feedback`

---

## **Typical Workflow**

1. Fetch new products from RSS feeds

2. Embed \+ store products in Redis Memory

3. For each subscribed user:

   a. Retrieve user taste profile

   b. Match products using semantic search

   c. Filter by preferences (brands, exclude disliked)

   d. Generate personalized email

   e. Send notification (respecting frequency settings)

4. Process feedback from email clicks

5. Update user preferences in Redis Memory

---

## **Error Handling**

* If RSS fetch fails → return empty product list, retry next cycle.

* If embeddings fail → skip that product.

* If user has no preferences yet → show general popular products.

* If email send fails → log error, retry next cycle.

* If preference update fails → log error, don't crash.

---

## **Output Requirements**

All agent-tool outputs should be concise, JSON-first, low token count, and reproducible.

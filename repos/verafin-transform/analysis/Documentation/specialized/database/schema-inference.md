# Database Schema Inference

**Project:** transform-jdo-demo  
**Database:** PostgreSQL  
**Analysis Method:** Inferred from SQL queries

---

## Table: users

**Purpose:** Store user account information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | User identifier |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| status | VARCHAR(20) | | Account status (ACTIVE, INACTIVE, SUSPENDED) |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Sample Data:**
```sql
INSERT INTO users (id, email, status) VALUES 
  ('user-001', 'alice@example.com', 'ACTIVE'),
  ('user-002', 'bob@example.com', 'INACTIVE');
```

---

## Table: invoices

**Purpose:** Store billing invoices

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment invoice ID |
| user_id | VARCHAR(50) | NOT NULL, FOREIGN KEY | Reference to users.id |
| amount | DECIMAL(10,2) | NOT NULL | Invoice amount |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp (inferred) |

**Foreign Keys:**
- `user_id` REFERENCES `users(id)`

**Sample Data:**
```sql
INSERT INTO invoices (user_id, amount) VALUES 
  ('user-001', 99.99),
  ('user-001', 199.99),
  ('user-002', 49.99);
```

---

## Entity Relationships

```
users (1) ────< invoices (many)
  id    ←────   user_id
```

**Relationship Type:** One-to-Many
- One user can have many invoices
- Each invoice belongs to one user

---

## Data Model Diagram

```
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ 🔑 id (PK)          │
│ 📧 email (UNIQUE)   │
│ 📊 status           │
└──────────┬──────────┘
           │ 1
           │
           │ *
┌──────────▼──────────┐
│     invoices        │
├─────────────────────┤
│ 🔑 id (PK)          │
│ 🔗 user_id (FK)     │
│ 💰 amount           │
│ 📅 created_at       │
└─────────────────────┘
```

---

*Last Updated: 2026-01-18*

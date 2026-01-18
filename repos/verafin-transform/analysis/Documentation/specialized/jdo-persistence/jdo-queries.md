# JDO Queries Catalog

**Project:** transform-jdo-demo  
**Total Queries:** 3

---

## 1. FIND_USER_BY_ID

**SQL:**
```sql
SELECT id, email, status FROM users WHERE id = :id
```

**Parameters:**
- `id` (String) - User identifier

**Returns:** User record or empty list

**Usage:** UserDao.findById()

---

## 2. UPDATE_EMAIL

**SQL:**
```sql
UPDATE users SET email = :email WHERE id = :id
```

**Parameters:**
- `id` (String) - User identifier
- `email` (String) - New email address

**Returns:** Number of rows updated

**Usage:** UserDao.updateEmail()

---

## 3. INSERT_INVOICE

**SQL:**
```sql
INSERT INTO invoices(user_id, amount) VALUES (:userId, :amount)
```

**Parameters:**
- `userId` (String) - User identifier
- `amount` (Double) - Invoice amount

**Returns:** Invoice ID

**Usage:** BillingService.createInvoice()

---

*Last Updated: 2026-01-18*

# Interface and Public API Documentation

**Generated from:** Static code analysis of transform-jdo-demo  
**Analysis Date:** 2026-01-18  
**Total Public Methods:** 18

## Table of Contents
1. [Overview](#overview)
2. [Public APIs by Component](#public-apis-by-component)
3. [API Contracts](#api-contracts)
4. [Parameter Specifications](#parameter-specifications)
5. [Return Value Specifications](#return-value-specifications)

---

## Overview

This document catalogs all **public methods** across the codebase. The system has **NO formal interfaces** defined - all contracts are implicit through public method signatures.

### API Design Characteristics
- **No Interface Declarations:** All APIs defined directly on concrete classes
- **Parameter Style:** Mix of primitives (String, int) and complex types (Map, BigDecimal)
- **Error Handling:** Return values (boolean, int, null) rather than exceptions
- **Transaction Management:** Explicit manual control (begin/commit/rollback)

---

## Public APIs by Component

### Summary Table

| Component | Public Methods | Complexity | Transaction Management |
|-----------|----------------|------------|------------------------|
| LegacyJdoManager | 5 | Low | Provides |
| LegacyQueries | 3 | Trivial | N/A |
| JdoPropertyKeys | 3 (constants) | Trivial | N/A |
| LegacyDbConfig | 3 | Trivial | N/A |
| UserRecord | 3 (auto-generated) | Trivial | N/A |
| UserDao | 2 | Medium | Uses |
| UserService | 1 | Medium | Manages |
| BillingService | 1 | Medium | Manages |

---

## 1. LegacyJdoManager APIs

**Class:** `com.transformtest.legacy.jdo.LegacyJdoManager`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/jdo/LegacyJdoManager.java`

### 1.1 executeUpdate
```java
public int executeUpdate(String sql, Map<String, Object> params)
```

**Purpose:** Execute SQL UPDATE, INSERT, or DELETE operations.

**Parameters:**
- `sql` - SQL statement with named parameters (e.g., `:id`, `:email`)
- `params` - Map of parameter names to values

**Returns:** 
- `int` - Number of rows affected (1-5 in deterministic mock implementation)

**Behavior:**
- Uses hash-based deterministic result generation (demo implementation)
- Actual implementation would execute SQL against database
- No validation of SQL or parameters

**Line Reference:** Line 14

**Example Usage:**
```java
Map<String, Object> params = new HashMap<>();
params.put("id", "u-123");
params.put("email", "new@example.com");
int rows = manager.executeUpdate(
    "UPDATE users SET email = :email WHERE id = :id", 
    params
);
```

---

### 1.2 executeQuery
```java
public List<Map<String, Object>> executeQuery(String sql, Map<String, Object> params)
```

**Purpose:** Execute SQL SELECT queries and return result rows.

**Parameters:**
- `sql` - SQL SELECT statement with named parameters
- `params` - Map of parameter names to values

**Returns:** 
- `List<Map<String, Object>>` - List of result rows, each row as column-name-to-value map
- Empty list if no results
- Never returns null

**Behavior:**
- Returns deterministic mock data for demo purposes
- Result includes columns: `id`, `email`, `status`
- Always returns at least one row with `status` = "ACTIVE"

**Line Reference:** Line 21

**Example Usage:**
```java
Map<String, Object> params = new HashMap<>();
params.put("id", "u-123");
List<Map<String, Object>> rows = manager.executeQuery(
    "SELECT id, email, status FROM users WHERE id = :id",
    params
);
```

---

### 1.3 begin
```java
public void begin()
```

**Purpose:** Start a new transaction.

**Parameters:** None

**Returns:** void

**Behavior:**
- Sets internal transaction state to "open"
- Stores state in concurrent map: `state.put("tx", "open")`
- No actual database transaction started (mock implementation)

**Line Reference:** Line 32

**Transaction Pattern:**
```java
manager.begin();
try {
    // ... database operations
    manager.commit();
} catch (Exception e) {
    manager.rollback();
}
```

---

### 1.4 commit
```java
public void commit()
```

**Purpose:** Commit the current transaction.

**Parameters:** None

**Returns:** void

**Behavior:**
- Removes transaction state from internal map: `state.remove("tx")`
- No actual database commit (mock implementation)
- Can be called multiple times without error

**Line Reference:** Line 33

---

### 1.5 rollback
```java
public void rollback()
```

**Purpose:** Rollback the current transaction.

**Parameters:** None

**Returns:** void

**Behavior:**
- Removes transaction state from internal map: `state.remove("tx")`
- No actual database rollback (mock implementation)
- Can be called multiple times without error

**Line Reference:** Line 34

---

## 2. LegacyQueries APIs

**Class:** `com.transformtest.legacy.jdo.LegacyQueries`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/jdo/LegacyQueries.java`

### 2.1 findUserById
```java
public static String findUserById()
```

**Purpose:** Return SQL query string for finding user by ID.

**Parameters:** None

**Returns:** 
- `String` - SQL: `"SELECT id, email, status FROM users WHERE id = :id"`

**Named Parameters:** `:id` (String user identifier)

**Line Reference:** Line 6

---

### 2.2 updateEmail
```java
public static String updateEmail()
```

**Purpose:** Return SQL query string for updating user email.

**Parameters:** None

**Returns:** 
- `String` - SQL: `"UPDATE users SET email = :email WHERE id = :id"`

**Named Parameters:** 
- `:email` (String new email address)
- `:id` (String user identifier)

**Line Reference:** Line 10

---

### 2.3 insertInvoice
```java
public static String insertInvoice()
```

**Purpose:** Return SQL query string for creating invoice.

**Parameters:** None

**Returns:** 
- `String` - SQL: `"INSERT INTO invoices(id, user_id, amount) VALUES (:id, :userId, :amount)"`

**Named Parameters:** 
- `:id` (String invoice identifier)
- `:userId` (String user identifier)
- `:amount` (BigDecimal invoice amount)

**Line Reference:** Line 14

---

## 3. JdoPropertyKeys APIs

**Class:** `com.transformtest.legacy.jdo.JdoPropertyKeys`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/jdo/JdoPropertyKeys.java`

### Public Constants

```java
public static final String CONNECTION_USER = "javax.jdo.option.ConnectionUserName"
public static final String CONNECTION_PWD = "javax.jdo.option.ConnectionPassword"
public static final String CONNECTION_URL = "javax.jdo.option.ConnectionURL"
```

**Purpose:** Standard JDO configuration property keys for JDBC connection.

**Usage:** Used with `System.getProperty()` to retrieve database credentials.

---

## 4. LegacyDbConfig APIs

**Class:** `com.acme.legacy.config.LegacyDbConfig`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/config/LegacyDbConfig.java`

### 4.1 user
```java
public static String user()
```

**Purpose:** Get database username from system properties or default.

**Parameters:** None

**Returns:** 
- `String` - Username (default: "legacy_user")

**System Property:** `javax.jdo.option.ConnectionUserName`

**Line Reference:** Line 8

---

### 4.2 password
```java
public static String password()
```

**Purpose:** Get database password from system properties or default.

**Parameters:** None

**Returns:** 
- `String` - Password (default: "legacy_pwd")

**System Property:** `javax.jdo.option.ConnectionPassword`

**Security Note:** ⚠️ Returns plaintext password, no encryption

**Line Reference:** Line 12

---

### 4.3 url
```java
public static String url()
```

**Purpose:** Get JDBC database URL from system properties or default.

**Parameters:** None

**Returns:** 
- `String` - JDBC URL (default: "jdbc:postgresql://localhost:5432/legacy")

**System Property:** `javax.jdo.option.ConnectionURL`

**Line Reference:** Line 16

---

## 5. UserRecord APIs

**Class:** `com.transformtest.legacy.user.UserRecord`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserRecord.java`

### Record Components (Auto-generated APIs)

```java
public record UserRecord(String id, String email, String status)
```

**Auto-Generated Methods (by Java Record):**

1. **Constructor:** `UserRecord(String id, String email, String status)`
2. **Accessor:** `String id()`
3. **Accessor:** `String email()`
4. **Accessor:** `String status()`
5. **equals(Object):** Structural equality
6. **hashCode():** Hash based on all fields
7. **toString():** String representation

**Line Reference:** Line 3

---

## 6. UserDao APIs

**Class:** `com.transformtest.legacy.user.UserDao`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserDao.java`

### 6.1 findById
```java
public UserRecord findById(String id)
```

**Purpose:** Find user by unique identifier.

**Parameters:**
- `id` - User identifier (String)

**Returns:** 
- `UserRecord` - User data if found
- `null` - If user doesn't exist

**Behavior:**
1. Creates parameter map with `id`
2. Executes SELECT query via LegacyJdoManager
3. Transforms first row to UserRecord
4. Returns null if no rows returned

**Dependencies:**
- LegacyJdoManager.executeQuery()
- LegacyQueries.findUserById()

**Error Handling:** No explicit error handling (relies on manager)

**Line Reference:** Lines 15-30

**Example Usage:**
```java
UserDao dao = new UserDao(manager);
UserRecord user = dao.findById("u-123");
if (user != null) {
    System.out.println("Found user: " + user.email());
}
```

---

### 6.2 updateEmail
```java
public int updateEmail(String id, String email)
```

**Purpose:** Update user's email address.

**Parameters:**
- `id` - User identifier (String)
- `email` - New email address (String)

**Returns:** 
- `int` - Number of rows updated (typically 1 or 0)

**Behavior:**
1. Creates parameter map with `id` and `email`
2. Executes UPDATE query via LegacyJdoManager
3. Returns row count from manager

**Dependencies:**
- LegacyJdoManager.executeUpdate()
- LegacyQueries.updateEmail()

**Error Handling:** No explicit error handling

**Line Reference:** Lines 32-37

**Example Usage:**
```java
UserDao dao = new UserDao(manager);
int rows = dao.updateEmail("u-123", "newemail@example.com");
System.out.println("Rows updated: " + rows);
```

---

## 7. UserService APIs

**Class:** `com.transformtest.legacy.user.UserService`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserService.java`

### 7.1 changeEmail
```java
public boolean changeEmail(String userId, String newEmail)
```

**Purpose:** Change user's email address with transaction management and validation.

**Parameters:**
- `userId` - User identifier (String)
- `newEmail` - New email address (String)

**Returns:** 
- `true` - Email successfully changed
- `false` - User not found OR exception occurred

**Transaction Behavior:**
- Starts transaction before operation
- Commits if successful
- Rolls back on any exception

**Business Logic:**
1. Begin transaction
2. Find user by ID
3. **Validate:** Return false if user not found
4. Update email via DAO
5. Commit transaction
6. Return success based on update count > 0

**Error Handling:**
- Catches all exceptions
- Rolls back transaction
- Returns false (suppresses exception)

**Cyclomatic Complexity:** 4

**Line Reference:** Lines 15-26

**Example Usage:**
```java
UserService service = new UserService(manager);
boolean success = service.changeEmail("u-123", "new@example.com");
if (success) {
    System.out.println("Email changed successfully");
} else {
    System.out.println("Failed to change email");
}
```

**API Contract Issues:**
- Cannot distinguish between "user not found" and "exception occurred"
- Suppresses all exceptions (no logging)
- No input validation (null checks, email format)

---

## 8. BillingService APIs

**Class:** `com.transformtest.legacy.billing.BillingService`  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/billing/BillingService.java`

### 8.1 createInvoice
```java
public int createInvoice(String invoiceId, String userId, BigDecimal amount)
```

**Purpose:** Create new invoice with transaction management.

**Parameters:**
- `invoiceId` - Invoice identifier (String)
- `userId` - User identifier (String)
- `amount` - Invoice amount (BigDecimal)

**Returns:** 
- `int` - Number of rows inserted (1 on success, 0 on failure)

**Transaction Behavior:**
- Starts transaction before operation
- Commits if successful
- Rolls back on any exception

**Business Logic:**
1. Begin transaction
2. Create parameter map with invoice data
3. Execute INSERT via LegacyJdoManager
4. Commit transaction
5. Return row count

**Error Handling:**
- Catches all exceptions
- Rolls back transaction
- Returns 0 (suppresses exception)

**Cyclomatic Complexity:** 3

**Line Reference:** Lines 18-31

**Example Usage:**
```java
BillingService service = new BillingService(manager);
int rows = service.createInvoice("inv-001", "u-123", new BigDecimal("99.99"));
if (rows > 0) {
    System.out.println("Invoice created successfully");
} else {
    System.out.println("Failed to create invoice");
}
```

**API Contract Issues:**
- Cannot distinguish between different failure modes
- Suppresses all exceptions (no logging)
- No input validation (null checks, amount validation)
- No duplicate invoice ID checking

---

## API Contracts

### Return Value Conventions

| Pattern | Classes | Meaning |
|---------|---------|---------|
| `boolean` | UserService | true = success, false = failure (any reason) |
| `int` | UserDao, BillingService, LegacyJdoManager | Row count affected (0 = failure/no match) |
| `UserRecord / null` | UserDao | Found entity or null for not found |
| `List` | LegacyJdoManager | Result rows (empty list if no results, never null) |
| `String` | LegacyQueries, LegacyDbConfig | Configuration values or SQL strings |

### Error Handling Patterns

1. **Exception Suppression (Anti-pattern):**
   - UserService.changeEmail() - catches all, returns false
   - BillingService.createInvoice() - catches all, returns 0
   - **Issue:** Caller cannot distinguish error types

2. **Null Returns:**
   - UserDao.findById() - returns null for not found
   - **Standard practice** but requires null checks

3. **No Validation:**
   - No input parameter validation in any API
   - No null checks before processing
   - No format validation (e.g., email format)

---

## Parameter Specifications

### Named Parameter Pattern

**Used by:** LegacyJdoManager, UserDao, BillingService

**Format:** Map<String, Object>

**Example:**
```java
Map<String, Object> params = new HashMap<>();
params.put("id", "u-123");
params.put("email", "user@example.com");
```

**Parameter Names by Query:**

**findUserById:**
- `:id` → String (user identifier)

**updateEmail:**
- `:id` → String (user identifier)
- `:email` → String (email address)

**insertInvoice:**
- `:id` → String (invoice identifier)
- `:userId` → String (user identifier)
- `:amount` → BigDecimal (invoice amount)

---

## Return Value Specifications

### Map-Based Result Rows

**Used by:** LegacyJdoManager.executeQuery()

**Format:** `List<Map<String, Object>>`

**Column Names (users table):**
- `"id"` → String
- `"email"` → String
- `"status"` → String

**Example:**
```java
List<Map<String, Object>> rows = manager.executeQuery(sql, params);
for (Map<String, Object> row : rows) {
    String id = String.valueOf(row.get("id"));
    String email = String.valueOf(row.get("email"));
    String status = String.valueOf(row.get("status"));
}
```

---

## Transaction Management APIs

### Manual Transaction Control

**Providers:** LegacyJdoManager  
**Consumers:** UserService, BillingService

**Required Pattern:**
```java
manager.begin();
try {
    // ... database operations
    manager.commit();
    return successValue;
} catch (Exception e) {
    manager.rollback();
    return failureValue;
}
```

**Issues:**
- No automatic transaction management
- Easy to forget begin/commit/rollback
- No nested transaction support
- No transaction isolation level control

---

## Related Documentation

- [Program Structure](program-structure.md)
- [Data Models](data-models.md)
- [Business Logic](../behavior/business-logic.md)
- [Error Handling Patterns](../behavior/error-handling.md)

---

*API documentation extracted through static code analysis.*

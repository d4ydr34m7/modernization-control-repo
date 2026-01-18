# Data Models and Parameter Mapping Documentation

**Generated from:** Static code analysis of transform-jdo-demo  
**Analysis Date:** 2026-01-18

## Table of Contents
1. [Overview](#overview)
2. [Domain Models](#domain-models)
3. [Parameter Mapping Patterns](#parameter-mapping-patterns)
4. [Database Schema Inference](#database-schema-inference)
5. [Data Transformation Patterns](#data-transformation-patterns)

---

## Overview

The codebase uses a **hybrid data representation strategy**:
- **Domain Models:** Java Records (UserRecord)
- **Database Layer:** Map<String, Object> (untyped parameter passing)
- **Queries:** Named parameter binding (`:paramName`)

This creates a **type-safe domain layer** with **type-unsafe persistence layer**.

---

## Domain Models

### UserRecord

**Package:** `com.transformtest.legacy.user`  
**Type:** Java Record (Immutable)  
**Source:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserRecord.java` (Line 3)

```java
public record UserRecord(String id, String email, String status) {}
```

**Components:**

| Field | Type | Purpose | Constraints |
|-------|------|---------|-------------|
| `id` | String | User unique identifier | Required, used as primary key |
| `email` | String | User email address | Required, should be unique |
| `status` | String | User account status | Required (e.g., "ACTIVE", "INACTIVE") |

**Characteristics:**
- ✅ **Immutable** - All fields final by record design
- ✅ **Type-safe** - Compile-time type checking
- ✅ **Auto-generated** - equals(), hashCode(), toString()
- ❌ **No validation** - Accepts null or invalid values
- ❌ **No business logic** - Pure data container

**Usage Pattern:**
```java
// Created from database query results
UserRecord user = new UserRecord("u-123", "user@example.com", "ACTIVE");

// Accessed via auto-generated accessors
String userId = user.id();
String email = user.email();
String status = user.status();
```

**Database Mapping:**
- Maps to `users` table (inferred)
- One-to-one field mapping with database columns

---

## Parameter Mapping Patterns

### Map-Based Parameter Passing

**Pattern:** `Map<String, Object>` for named parameters  
**Used in:** All database operations via LegacyJdoManager

#### Characteristics
- **Type:** `java.util.HashMap<String, Object>`
- **Purpose:** Pass named parameters to SQL queries
- **Binding:** Named parameters in SQL (`:paramName`)
- **Type Safety:** ❌ None - values are Object type
- **Validation:** ❌ None - no parameter validation

---

### Parameter Mapping by Operation

#### 1. Find User By ID

**Method:** `UserDao.findById(String id)`  
**Source:** Lines 15-17 in UserDao.java

**Parameter Map Construction:**
```java
Map<String, Object> p = new HashMap<>();
p.put("id", id);
```

**SQL Named Parameters:**
- `:id` → String (user identifier)

**Query:** `SELECT id, email, status FROM users WHERE id = :id`

---

#### 2. Update Email

**Method:** `UserDao.updateEmail(String id, String email)`  
**Source:** Lines 32-35 in UserDao.java

**Parameter Map Construction:**
```java
Map<String, Object> p = new HashMap<>();
p.put("id", id);
p.put("email", email);
```

**SQL Named Parameters:**
- `:id` → String (user identifier)
- `:email` → String (new email address)

**Query:** `UPDATE users SET email = :email WHERE id = :id`

---

#### 3. Create Invoice

**Method:** `BillingService.createInvoice(String invoiceId, String userId, BigDecimal amount)`  
**Source:** Lines 20-23 in BillingService.java

**Parameter Map Construction:**
```java
Map<String, Object> p = new HashMap<>();
p.put("id", invoiceId);
p.put("userId", userId);
p.put("amount", amount);
```

**SQL Named Parameters:**
- `:id` → String (invoice identifier)
- `:userId` → String (user reference)
- `:amount` → BigDecimal (invoice amount)

**Query:** `INSERT INTO invoices(id, user_id, amount) VALUES (:id, :userId, :amount)`

---

## Database Schema Inference

### Inferred Schema from Queries

#### Users Table

**Table Name:** `users`  
**Inferred from:** LegacyQueries.findUserById(), LegacyQueries.updateEmail()

| Column | Type | Constraints | Usage |
|--------|------|-------------|-------|
| `id` | String/VARCHAR | PRIMARY KEY | User identifier |
| `email` | String/VARCHAR | NOT NULL, likely UNIQUE | User email address |
| `status` | String/VARCHAR | NOT NULL | Account status ("ACTIVE", etc.) |

**SQL Operations:**
- SELECT: `LegacyQueries.findUserById()` (Line 6)
- UPDATE: `LegacyQueries.updateEmail()` (Line 10)

**Java Mapping:** UserRecord(id, email, status)

---

#### Invoices Table

**Table Name:** `invoices`  
**Inferred from:** LegacyQueries.insertInvoice()

| Column | Type | Constraints | Usage |
|--------|------|-------------|-------|
| `id` | String/VARCHAR | PRIMARY KEY | Invoice identifier |
| `user_id` | String/VARCHAR | FOREIGN KEY → users.id | User reference |
| `amount` | NUMERIC/DECIMAL | NOT NULL | Invoice amount |

**SQL Operations:**
- INSERT: `LegacyQueries.insertInvoice()` (Line 14)

**Java Mapping:** No Java entity (parameters only)

---

### Entity Relationships

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK)         │──┐
│ email           │  │
│ status          │  │
└─────────────────┘  │
                     │ 1:N
                     │
                ┌────▼──────────┐
                │   invoices    │
                │───────────────│
                │ id (PK)       │
                │ user_id (FK)  │
                │ amount        │
                └───────────────┘
```

**Relationship:** One User to Many Invoices (1:N)

---

## Data Transformation Patterns

### Pattern 1: Map to Domain Model

**Location:** `UserDao.findById()` (Lines 24-28)  
**Purpose:** Transform database result row to typed UserRecord

**Source (Database Result):**
```java
Map<String, Object> r = rows.get(0);
// Example: {
//   "id": "u-123",
//   "email": "user@example.com",
//   "status": "ACTIVE"
// }
```

**Transformation Logic:**
```java
return new UserRecord(
    String.valueOf(r.get("id")),      // Line 25
    String.valueOf(r.get("email")),   // Line 26
    String.valueOf(r.get("status"))   // Line 27
);
```

**Target (Domain Model):**
```java
UserRecord(id="u-123", email="user@example.com", status="ACTIVE")
```

**Transformation Steps:**
1. Extract first row from result list
2. Get values by column name
3. Convert to String using String.valueOf()
4. Create immutable UserRecord

**Type Safety Issues:**
- `String.valueOf()` on Object - could be null → "null" string
- No validation of expected columns
- ClassCastException possible if types don't match

---

### Pattern 2: Domain Parameters to Map

**Location:** `UserDao.updateEmail()` (Lines 32-35)  
**Purpose:** Transform typed method parameters to Map for SQL execution

**Source (Method Parameters):**
```java
String id = "u-123";
String email = "new@example.com";
```

**Transformation Logic:**
```java
Map<String, Object> p = new HashMap<>();
p.put("id", id);
p.put("email", email);
```

**Target (Parameter Map):**
```java
{"id": "u-123", "email": "new@example.com"}
```

**Type Safety Issues:**
- Manual string key entry - typo risk
- No compile-time checking of parameter names
- Values as Object - type erasure

---

### Pattern 3: Business Parameters to Map

**Location:** `BillingService.createInvoice()` (Lines 20-23)  
**Purpose:** Package complex business data for database operation

**Source (Method Parameters):**
```java
String invoiceId = "inv-001";
String userId = "u-123";
BigDecimal amount = new BigDecimal("99.99");
```

**Transformation Logic:**
```java
Map<String, Object> p = new HashMap<>();
p.put("id", invoiceId);
p.put("userId", userId);
p.put("amount", amount);
```

**Target (Parameter Map):**
```java
{
  "id": "inv-001",
  "userId": "u-123",
  "amount": BigDecimal("99.99")
}
```

**Column Name Mapping:**
- Map key `"userId"` → SQL parameter `:userId` → Column `user_id`
- Inconsistent naming convention (camelCase vs snake_case)

---

## Data Type Mapping

### Java to SQL Type Mapping

| Java Type | SQL Type (PostgreSQL) | Usage |
|-----------|----------------------|-------|
| String | VARCHAR / TEXT | User IDs, emails, status |
| BigDecimal | NUMERIC / DECIMAL | Invoice amounts |
| Object | ANY (type-unsafe) | Generic parameter passing |

**Notes:**
- No explicit type mapping code (inferred from usage)
- BigDecimal appropriate for financial data (precise decimal arithmetic)
- String used for identifiers (not numeric IDs)

---

## Parameter Validation Issues

### Missing Validations

| Validation Type | Impact | Affected APIs |
|-----------------|--------|---------------|
| **Null checks** | NullPointerException risk | All methods |
| **Email format** | Invalid data stored | UserDao.updateEmail() |
| **Amount validation** | Negative/zero amounts | BillingService.createInvoice() |
| **ID format** | Inconsistent identifiers | All ID parameters |
| **Parameter name typos** | SQL parameter binding failures | All Map-based operations |

**Example Risk:**
```java
// No validation - will fail at database layer
service.createInvoice(null, null, null);

// No validation - invalid email accepted
dao.updateEmail("u-123", "not-an-email");

// No validation - negative amount accepted
service.createInvoice("inv-1", "u-1", new BigDecimal("-100"));
```

---

## Data Model Anti-Patterns

### 1. Type-Unsafe Parameter Passing
**Issue:** Map<String, Object> loses compile-time type safety  
**Risk:** Type mismatches discovered at runtime  
**Better Approach:** Type-safe parameter objects or builder pattern

### 2. String-Based Column References
**Issue:** Column names as strings ("id", "email") - typo risk  
**Risk:** Runtime failures from incorrect column names  
**Better Approach:** Constants or enums for column names

### 3. Manual Result Mapping
**Issue:** Manual transformation from Map to UserRecord  
**Risk:** Boilerplate code, mapping errors  
**Better Approach:** ORM framework (JPA, Hibernate) with automatic mapping

### 4. No Data Validation
**Issue:** No validation at domain model or parameter level  
**Risk:** Invalid data persisted to database  
**Better Approach:** Bean Validation (JSR-380) or custom validators

### 5. Mixed Naming Conventions
**Issue:** Java camelCase (userId) vs SQL snake_case (user_id)  
**Risk:** Confusion, mapping errors  
**Better Approach:** Consistent naming or explicit mapping configuration

---

## Data Flow Summary

```
Service Layer (Type-safe)
    ↓
Method Parameters (String, BigDecimal, etc.)
    ↓
Map<String, Object> Construction (Type-unsafe)
    ↓
LegacyJdoManager (Generic execution)
    ↓
SQL with Named Parameters (:paramName)
    ↓
Database (PostgreSQL)
    ↓
Result: List<Map<String, Object>> (Type-unsafe)
    ↓
Manual Mapping to UserRecord (Type-safe)
    ↓
Service Layer Returns (Type-safe)
```

**Type Safety Boundary:** Between service parameters and Map construction

---

## Configuration Data Model

### System Property Based Configuration

**Class:** `LegacyDbConfig`  
**Pattern:** Static methods returning configuration strings

**Configuration Model:**
```java
{
  "javax.jdo.option.ConnectionUserName": "legacy_user",
  "javax.jdo.option.ConnectionPassword": "legacy_pwd",
  "javax.jdo.option.ConnectionURL": "jdbc:postgresql://localhost:5432/legacy"
}
```

**Access Pattern:**
```java
String dbUser = LegacyDbConfig.user();
String dbPassword = LegacyDbConfig.password();
String dbUrl = LegacyDbConfig.url();
```

**Issues:**
- Credentials in system properties (not environment variables)
- Default credentials hardcoded in source
- No encryption or secrets management

---

## Related Documentation

- [Program Structure](program-structure.md)
- [Interfaces and APIs](interfaces.md)
- [Database Schema Inference](../specialized/database/schema-inference.md)
- [Security Patterns](../analysis/security-patterns.md)

---

*Data model documentation extracted through static code analysis.*

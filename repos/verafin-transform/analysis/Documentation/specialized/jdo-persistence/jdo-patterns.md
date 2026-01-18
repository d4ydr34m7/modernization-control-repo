# JDO Patterns Documentation

**Project:** transform-jdo-demo  
**Technology:** Java Data Objects (JDO) API 3.1  
**Status:** 🔴 DEPRECATED - Migrate to JPA

---

## JDO Usage Patterns in Codebase

### 1. LegacyJdoManager Pattern

**Purpose:** Wrapper around JDO persistence operations

**Implementation:**
```java
public class LegacyJdoManager {
  private final Map<String, Object> state = new ConcurrentHashMap<>();
  
  public int executeUpdate(String sql, Map<String, Object> params) {
    // Executes SQL update with parameters
    return rowsAffected;
  }
  
  public List<Map<String, Object>> executeQuery(String sql, Map<String, Object> params) {
    // Executes SQL query with parameters
    return results;
  }
  
  public void begin() { state.put("tx", "open"); }
  public void commit() { state.remove("tx"); }
  public void rollback() { state.remove("tx"); }
}
```

**Issues:**
- Stateful design (ConcurrentHashMap)
- Manual transaction management
- Type-unsafe Map<String, Object> returns

---

### 2. Query Execution Pattern

**Pattern:** Named parameters in raw SQL

**Example:**
```java
String sql = "SELECT id, email, status FROM users WHERE id = :id";
Map<String, Object> params = Map.of("id", userId);
List<Map<String, Object>> results = manager.executeQuery(sql, params);
```

**Benefits:**
- SQL injection protection via parameterization
- Explicit parameter mapping

**Issues:**
- Type-unsafe Map<String, Object>
- Manual result mapping required

---

### 3. Transaction Management Pattern

**Pattern:** Manual begin/commit/rollback

**Example:**
```java
manager.begin();
try {
  // Database operations
  manager.commit();
} catch (Exception e) {
  manager.rollback();
  // Error handling
}
```

**Issues:**
- Requires manual transaction boundaries
- Easy to forget rollback
- Exception suppression common

---

### 4. Parameter Mapping Convention

**Convention:** Map keys match SQL named parameters

**Example:**
```java
// SQL: "INSERT INTO invoices(user_id, amount) VALUES (:userId, :amount)"
Map<String, Object> params = Map.of(
  "userId", "user-123",
  "amount", 99.99
);
```

**Issues:**
- No compile-time validation
- Typos in keys cause runtime errors
- Type mismatches discovered at runtime

---

## Migration Path to JPA

See [JDO Migration Guide](jdo-migration-guide.md) for detailed migration instructions.

---

*Last Updated: 2026-01-18*

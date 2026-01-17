# Public Interfaces and API Contracts

## Overview
This document describes all public interfaces, APIs, and contracts exposed by the Legacy Java Demo codebase. It serves as a reference for understanding the public surface area and integration points.

## Important Note: No Formal Interfaces
This codebase **does not define any Java interfaces** using the `interface` keyword. All components are concrete classes with public methods that constitute the de facto API surface.

---

## Public API Surface

### Package: com.verafin.commons.jdo

#### API: LegacyJdoManager (Transaction Management)

**Contract**: Provides transaction lifecycle management for JDO operations

##### API Methods

###### begin()
```java
public void begin()
```
- **Purpose**: Begin a new transaction
- **Preconditions**: No active transaction (typically)
- **Postconditions**: Transaction is active and ready for operations
- **Thread Safety**: Unclear - likely not thread-safe (typical JDO pattern is one transaction per thread)
- **Usage Example**:
```java
LegacyJdoManager jdo = new LegacyJdoManager();
jdo.begin();
// ... perform operations ...
jdo.commit();
```

###### commit()
```java
public void commit()
```
- **Purpose**: Commit the current transaction
- **Preconditions**: Active transaction exists
- **Postconditions**: Changes are persisted, transaction is closed
- **Exceptions**: May throw exceptions if commit fails (not documented in stub)
- **Usage Example**:
```java
jdo.begin();
try {
    // ... operations ...
    jdo.commit();
} catch (Exception e) {
    jdo.rollback();
    throw e;
}
```

###### rollback()
```java
public void rollback()
```
- **Purpose**: Roll back the current transaction
- **Preconditions**: Active transaction exists
- **Postconditions**: Changes are discarded, transaction is closed
- **Usage Context**: Called in exception handlers
- **Usage Example**:
```java
jdo.begin();
try {
    // ... operations ...
    jdo.commit();
} catch (RuntimeException e) {
    jdo.rollback();
    throw e;
}
```

**API Stability**: ⚠️ Internal API - Subject to change during JDO-to-JPA migration

---

#### API: LegacyQueries (Query Construction)

**Contract**: Provides utility methods for constructing JDO query strings

##### API Methods

###### byCustomerId(String id)
```java
public static String byCustomerId(String id)
```
- **Purpose**: Construct JDOQL query string for finding customer by ID
- **Parameters**:
  - `id` - Customer identifier (required, non-null expected)
- **Returns**: JDOQL query string in format: `SELECT FROM com.verafin.legacy.Customer WHERE id == '<id>'`
- **Thread Safety**: Yes (stateless static method)
- **⚠️ Security Warning**: Vulnerable to injection attacks - id parameter is directly concatenated
- **Usage Example**:
```java
String query = LegacyQueries.byCustomerId("CUST-001");
// Returns: "SELECT FROM com.verafin.legacy.Customer WHERE id == 'CUST-001'"
```

**Security Recommendation**: Replace with parameterized queries:
```java
// Recommended approach (JPA/JPQL)
String query = "SELECT c FROM Customer c WHERE c.id = :id";
// Then bind parameter separately
```

**API Stability**: ⚠️ Deprecated - Will be replaced during migration to JPA

---

### Package: com.verafin.legacy

#### API: Customer (Entity/Value Object)

**Contract**: Immutable representation of customer data

##### Constructor API

###### Customer(String id, String name)
```java
public Customer(String id, String name)
```
- **Purpose**: Create new Customer instance
- **Parameters**:
  - `id` - Unique customer identifier (required, non-null)
  - `name` - Customer name (required, non-null)
- **Immutability**: All fields are final; object is immutable after construction
- **Thread Safety**: Yes (immutable)
- **Validation**: ⚠️ None - accepts any strings including nulls
- **Usage Example**:
```java
Customer customer = new Customer("CUST-123", "John Doe");
```

##### Accessor API

###### getId()
```java
public String getId()
```
- **Purpose**: Retrieve customer unique identifier
- **Returns**: Customer ID string
- **Thread Safety**: Yes (immutable field)
- **Nullability**: Depends on constructor input (no validation)

###### getName()
```java
public String getName()
```
- **Purpose**: Retrieve customer name
- **Returns**: Customer name string
- **Thread Safety**: Yes (immutable field)
- **Nullability**: Depends on constructor input (no validation)

**Usage Example**:
```java
Customer c = new Customer("1", "Shreya");
String id = c.getId();     // "1"
String name = c.getName(); // "Shreya"
```

**API Stability**: ✅ Stable - Core domain model

**Persistence Contract**:
- Annotated with `@PersistenceCapable` - JDO will manage persistence
- `id` field annotated with `@PrimaryKey` - Defines primary key
- Must maintain no-arg constructor for JDO (not present - potential issue)

---

#### API: CustomerDao (Data Access)

**Contract**: Provides data access operations for Customer entities

##### Constructor API

###### CustomerDao(LegacyJdoManager jdo)
```java
public CustomerDao(LegacyJdoManager jdo)
```
- **Purpose**: Create CustomerDao with transaction manager
- **Parameters**:
  - `jdo` - Transaction manager instance (required, non-null expected)
- **Pattern**: Constructor-based dependency injection
- **Usage Example**:
```java
LegacyJdoManager jdo = new LegacyJdoManager();
CustomerDao dao = new CustomerDao(jdo);
```

##### Data Access API

###### buildFindByIdQuery(String id)
```java
public String buildFindByIdQuery(String id)
```
- **Purpose**: Build JDO query string for finding customer by ID
- **Parameters**:
  - `id` - Customer identifier to search for (required)
- **Returns**: JDOQL query string
- **Note**: Query construction only; not executed in this demo
- **Thread Safety**: Depends on LegacyQueries implementation (stateless, so yes)
- **⚠️ Security Warning**: Inherits injection vulnerability from LegacyQueries
- **Usage Example**:
```java
CustomerDao dao = new CustomerDao(jdo);
String query = dao.buildFindByIdQuery("CUST-001");
// Would typically be followed by: execute query and return Customer
```

**Expected Future API** (for complete implementation):
```java
// Not yet implemented - would look like:
public Customer findById(String id) {
    jdo.begin();
    try {
        String query = buildFindByIdQuery(id);
        Customer result = executeQuery(query);
        jdo.commit();
        return result;
    } catch (Exception e) {
        jdo.rollback();
        throw e;
    }
}
```

**API Stability**: ⚠️ Incomplete - Query building without execution

---

#### API: CustomerService (Business Logic)

**Contract**: Provides business operations for customer management

##### Constructor API

###### CustomerService(LegacyJdoManager jdo)
```java
public CustomerService(LegacyJdoManager jdo)
```
- **Purpose**: Create CustomerService with transaction manager
- **Parameters**:
  - `jdo` - Transaction manager instance (required, non-null expected)
- **Pattern**: Constructor-based dependency injection
- **Usage Example**:
```java
LegacyJdoManager jdo = new LegacyJdoManager();
CustomerService service = new CustomerService(jdo);
```

##### Business Logic API

###### formatDisplay(Customer c)
```java
public String formatDisplay(Customer c)
```
- **Purpose**: Format customer data for display with transaction management
- **Parameters**:
  - `c` - Customer entity to format (required, non-null expected)
- **Returns**: Formatted string in format `{id}:{name}`
- **Format Specification**: `{customer.id}:{customer.name}` (colon-separated)
- **Transaction Behavior**: 
  - Begins transaction before formatting
  - Commits transaction on success
  - Rolls back transaction on exception
- **Exceptions**: 
  - Throws RuntimeException if formatting fails
  - Original exception is propagated after rollback
- **Thread Safety**: Not thread-safe (transaction state in jdo)
- **Usage Example**:
```java
CustomerService service = new CustomerService(jdo);
Customer customer = new Customer("1", "Shreya");
String display = service.formatDisplay(customer);
// Returns: "1:Shreya"
```

**Business Rule**: Customer display format is `id:name` with colon separator

**API Stability**: ⚠️ Questionable design - transaction management for read-only formatting

---

## API Contracts Summary

### Constructor Injection Pattern
All service and DAO classes use constructor-based dependency injection:
```java
// Pattern used throughout codebase
public class ServiceOrDao {
    private final Dependency dep;
    
    public ServiceOrDao(Dependency dep) {
        this.dep = dep;
    }
}
```

**Benefits**:
- Explicit dependencies
- Immutable dependency references (final fields)
- Easy to test (pass mock dependencies)

---

## Transaction Management Contract

### Standard Transaction Pattern
```java
jdo.begin();
try {
    // ... perform operations ...
    jdo.commit();
} catch (RuntimeException e) {
    jdo.rollback();
    throw e;
}
```

**Used in**: CustomerService.formatDisplay()

**Contract Requirements**:
1. Always call `begin()` before operations
2. Always call `commit()` on success
3. Always call `rollback()` in exception handlers
4. Always propagate exceptions after rollback

---

## API Limitations and Gaps

### Missing Validation
- No null checks on parameters
- No validation of input data (e.g., empty strings)
- No precondition assertions

### Missing Error Handling
- No checked exceptions defined
- No error codes or status returns
- No detailed exception types

### Missing Contracts
- No formal interfaces defined
- No documented service contracts (JSR-305, annotations)
- No API versioning

### Missing Features
- No pagination support
- No batch operations
- No async/reactive APIs
- No query result execution (only query building)

---

## API Evolution Recommendations

### Short Term (Maintain Compatibility)
1. Add null validation to all public methods
2. Document expected exceptions
3. Add JavaDoc to all public methods
4. Define parameter constraints

### Medium Term (Migration)
1. Extract interfaces for testability
```java
public interface TransactionManager {
    void begin();
    void commit();
    void rollback();
}

public class LegacyJdoManager implements TransactionManager { ... }
```

2. Replace JDO with JPA
```java
public interface CustomerRepository {
    Optional<Customer> findById(String id);
    Customer save(Customer customer);
}
```

3. Use parameterized queries
```java
@Query("SELECT c FROM Customer c WHERE c.id = :id")
Customer findById(@Param("id") String id);
```

### Long Term (Modern API)
1. Adopt Spring Data repositories
2. Use declarative transaction management (`@Transactional`)
3. Implement REST APIs
4. Add async support (CompletableFuture, reactive streams)

---

## API Compatibility Matrix

### Public API Changes During Migration

| Current API | JPA Equivalent | Breaking Change? |
|-------------|---------------|------------------|
| LegacyJdoManager | EntityManager | Yes - Different interface |
| LegacyQueries | JPQL/Criteria API | Yes - Different approach |
| Customer entity | JPA @Entity | Minor - Annotation changes |
| CustomerDao | Spring Data Repository | Yes - New interface pattern |
| CustomerService | Same | No - Business logic unchanged |

---

## Cross-References

### Related Documentation
- [Program Structure](program-structure.md) - Detailed class documentation
- [Data Models](data-models.md) - Entity contracts and persistence
- [Business Logic](../behavior/business-logic.md) - Business rule implementation
- [API Reference](api-reference.md) - Complete API documentation
- [Migration Guide](../migration/component-order.md) - API migration strategy
- [Technical Debt](../technical-debt-report.md) - API limitations and issues

---

*Generated by Comprehensive Codebase Analysis*  
*Last Updated: 2026-01-16*  
*Source: Static analysis of public methods across 5 Java classes*

# Data Models and Entity Reference

## Overview
This document provides comprehensive documentation of all data models, entities, and their relationships in the Legacy Java Demo codebase. It covers entity structure, persistence mappings, field specifications, and data relationships.

---

## Entity Inventory

### Total Entities: 1
- **Customer** - Core domain entity representing customer data

### Persistence Framework: JDO (Java Data Objects)
- Annotation-based configuration
- javax.jdo:jdo-api:3.1

---

## Entity: Customer

### Overview
**Package**: `com.verafin.legacy`  
**File**: `legacy-app/src/main/java/com/verafin/legacy/Customer.java`  
**Purpose**: Represents customer data in the system  
**Persistence**: JDO-managed persistent entity  
**Immutability**: Immutable (all fields final)

### Entity Declaration
```java
package com.verafin.legacy;

import javax.jdo.annotations.PersistenceCapable;
import javax.jdo.annotations.PrimaryKey;

@PersistenceCapable
public class Customer {
    @PrimaryKey
    private final String id;
    private final String name;
    
    public Customer(String id, String name) {
        this.id = id;
        this.name = name;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
}
```

---

## Field Specifications

### Field: id
**Data Type**: String  
**Database Role**: Primary Key  
**Mutability**: Immutable (final)  
**Nullability**: Not specified (⚠️ no validation)  
**Annotations**: `@PrimaryKey`

#### Persistence Mapping
- **JDO Annotation**: `@PrimaryKey`
- **Database Column**: Typically mapped to "ID" or "CUSTOMER_ID"
- **Index**: Primary key index (automatic)
- **Uniqueness**: Enforced by primary key constraint

#### Characteristics
- **Length**: Unbounded (String - no @Column constraints)
- **Format**: Not specified (accepts any string)
- **Generation**: Application-assigned (no auto-generation)
- **Business Meaning**: Unique customer identifier

#### Usage
```java
Customer c = new Customer("CUST-001", "John Doe");
String id = c.getId(); // "CUST-001"
```

#### Migration Notes
JPA equivalent would be:
```java
@Id
@Column(name = "id", nullable = false, length = 50)
private String id;
```

---

### Field: name
**Data Type**: String  
**Database Role**: Regular column  
**Mutability**: Immutable (final)  
**Nullability**: Not specified (⚠️ no validation)  
**Annotations**: None

#### Persistence Mapping
- **JDO Annotation**: None (default persistence)
- **Database Column**: Typically mapped to "NAME"
- **Index**: None (not specified)

#### Characteristics
- **Length**: Unbounded (String - no @Column constraints)
- **Format**: Not specified (accepts any string)
- **Business Meaning**: Customer name

#### Usage
```java
Customer c = new Customer("CUST-001", "Jane Smith");
String name = c.getName(); // "Jane Smith"
```

#### Migration Notes
JPA equivalent would be:
```java
@Column(name = "name", nullable = false, length = 255)
private String name;
```

---

## Persistence Configuration

### JDO Annotations

#### @PersistenceCapable
**Target**: Class level  
**Purpose**: Marks Customer class as persistable by JDO

**Attributes** (none explicitly set - using defaults):
- `table`: Default (class name "Customer")
- `schema`: Default
- `catalog`: Default
- `identityType`: APPLICATION (inferred from @PrimaryKey)
- `cacheable`: Default (likely true)

**Full annotation options** (not used):
```java
@PersistenceCapable(
    table = "CUSTOMERS",
    schema = "PUBLIC",
    identityType = IdentityType.APPLICATION
)
```

#### @PrimaryKey
**Target**: Field level (id)  
**Purpose**: Designates id field as the primary key

**Characteristics**:
- Single-field primary key
- String type (uncommon - usually numeric)
- Application-assigned (no generator)

**Full annotation options** (not used):
```java
@PrimaryKey
@Column(name = "CUSTOMER_ID", jdbcType = "VARCHAR", length = 50)
```

---

## Entity Relationships

### Current State: No Relationships
The Customer entity has **no explicit relationships** to other entities in this codebase.

#### Missing Relationships (Potential Future Extensions)
- **Orders**: One-to-Many relationship with Order entity
- **Addresses**: One-to-Many relationship with Address entity
- **ContactInfo**: One-to-One relationship with ContactInfo entity
- **Account**: Many-to-One relationship with Account entity

#### Example Future Relationship (JDO)
```java
@PersistenceCapable
public class Customer {
    @PrimaryKey
    private String id;
    
    private String name;
    
    @Persistent(mappedBy = "customer")
    private List<Order> orders; // One-to-Many
}
```

#### Example Future Relationship (JPA)
```java
@Entity
public class Customer {
    @Id
    private String id;
    
    private String name;
    
    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL)
    private List<Order> orders;
}
```

---

## Data Validation

### Current Validation: None ⚠️

#### Missing Validations
1. **Null checks**: No validation that id or name are non-null
2. **Empty string checks**: No validation that values are non-empty
3. **Length constraints**: No maximum length enforcement
4. **Format validation**: No regex or format requirements
5. **Business rule validation**: No domain-specific rules

#### Recommended Validations (JPA/Bean Validation)
```java
import javax.validation.constraints.*;

@Entity
public class Customer {
    @Id
    @NotNull(message = "Customer ID cannot be null")
    @Size(min = 1, max = 50, message = "Customer ID must be 1-50 characters")
    @Pattern(regexp = "^[A-Z0-9-]+$", message = "Invalid ID format")
    private String id;
    
    @NotNull(message = "Customer name cannot be null")
    @Size(min = 1, max = 255, message = "Customer name must be 1-255 characters")
    private String name;
}
```

---

## Entity Lifecycle

### Creation
```java
// Customer creation (immutable)
Customer customer = new Customer("CUST-001", "John Doe");
// Fields cannot be changed after construction
```

### Persistence (Conceptual - not implemented in demo)
```java
// Typical JDO persistence
PersistenceManager pm = pmf.getPersistenceManager();
Transaction tx = pm.currentTransaction();
try {
    tx.begin();
    pm.makePersistent(customer); // Persist new customer
    tx.commit();
} finally {
    if (tx.isActive()) {
        tx.rollback();
    }
    pm.close();
}
```

### Retrieval (Conceptual - not implemented)
```java
// Query by ID (using query string from CustomerDao)
String query = LegacyQueries.byCustomerId("CUST-001");
// Execute query to retrieve Customer
```

### Update (Not Possible - Immutable)
```java
// Cannot update - all fields are final
// Would need to create new instance
Customer updated = new Customer(customer.getId(), "New Name");
```

### Deletion (Conceptual - not implemented)
```java
// Typical JDO deletion
pm.deletePersistent(customer);
```

---

## Data Type Mapping

### Java to Database Type Mapping

| Java Type | JDO Default | Typical SQL Type | Notes |
|-----------|-------------|------------------|-------|
| String (id) | VARCHAR | VARCHAR(255) | Primary key, may need size constraint |
| String (name) | VARCHAR | VARCHAR(255) | May need size constraint |

### JPA Migration Type Mapping
```java
@Entity
@Table(name = "customer")
public class Customer {
    @Id
    @Column(name = "id", columnDefinition = "VARCHAR(50)")
    private String id;
    
    @Column(name = "name", columnDefinition = "VARCHAR(255)")
    private String name;
}
```

---

## Immutability Pattern

### Design: Value Object Pattern
Customer entity follows the **immutable value object** pattern:

#### Characteristics
1. **All fields are final** - Cannot be modified after construction
2. **No setter methods** - Only getters provided
3. **Constructor initialization** - All data provided at creation
4. **Thread-safe** - Immutability ensures thread safety

#### Benefits
- Thread safety without synchronization
- No defensive copying needed
- Predictable behavior
- Cacheable (safe to share references)

#### Drawbacks for ORM
- **⚠️ JDO/JPA Problem**: Most ORMs require no-arg constructor and setters
- **⚠️ Proxy Problem**: ORMs use proxies that may not work with final fields
- **⚠️ Lazy Loading Problem**: Cannot lazy-load relationships with final fields

#### Potential Issue
```java
// JDO typically requires:
public class Customer {
    private String id; // Non-final
    private String name; // Non-final
    
    public Customer() {} // No-arg constructor
    
    // Setters for JDO to populate fields
    public void setId(String id) { this.id = id; }
    public void setName(String name) { this.name = name; }
}
```

---

## Query Targeting

### JDOQL Query Pattern
```java
// From LegacyQueries.byCustomerId()
String query = "SELECT FROM com.verafin.legacy.Customer WHERE id == '" + id + "'";
```

#### Query Analysis
- **Target Class**: `com.verafin.legacy.Customer`
- **Filter**: `id == '<value>'`
- **Result Type**: Single Customer or collection
- **⚠️ Security Issue**: SQL injection vulnerability

### Safe Query Alternative (JPA)
```java
// JPQL with named parameter
String jpql = "SELECT c FROM Customer c WHERE c.id = :customerId";
TypedQuery<Customer> query = em.createQuery(jpql, Customer.class);
query.setParameter("customerId", id);
Customer result = query.getSingleResult();
```

---

## Entity Metadata Summary

### Customer Entity Metadata

| Attribute | Value |
|-----------|-------|
| **Class Name** | Customer |
| **Package** | com.verafin.legacy |
| **Persistence Type** | JDO Entity |
| **Table Name** | customer (default) |
| **Primary Key** | id (String) |
| **Fields** | 2 (id, name) |
| **Relationships** | 0 |
| **Constraints** | Primary key only |
| **Indexes** | Primary key index |
| **Mutability** | Immutable |
| **Thread Safety** | Yes (immutable) |
| **Validation** | None ⚠️ |

---

## Domain Model Concepts

### Customer Aggregate
```
Customer (Aggregate Root)
    └── No child entities (currently)
```

### Bounded Context
**Context**: Customer Management  
**Entities**: Customer  
**Value Objects**: None explicitly defined  
**Services**: CustomerService, CustomerDao

---

## Data Dictionary

### Entity: Customer

| Field | Type | Required | Unique | Default | Description |
|-------|------|----------|--------|---------|-------------|
| id | String | Yes* | Yes | None | Unique customer identifier |
| name | String | Yes* | No | None | Customer name |

*Not enforced by validation, but required by business logic

---

## Migration Considerations

### JDO to JPA Migration

#### Annotation Changes
```java
// JDO
@PersistenceCapable
public class Customer {
    @PrimaryKey
    private String id;
}

// JPA
@Entity
public class Customer {
    @Id
    private String id;
}
```

#### Required Changes
1. Replace `@PersistenceCapable` with `@Entity`
2. Replace `@PrimaryKey` with `@Id`
3. Add `@Table` annotation (optional but recommended)
4. Add `@Column` annotations for constraints
5. Add validation annotations
6. Consider adding no-arg constructor (required by JPA)
7. Consider making fields non-final (required by JPA)

#### Complete Migrated Entity
```java
@Entity
@Table(name = "customer")
public class Customer implements Serializable {
    @Id
    @Column(name = "id", nullable = false, length = 50)
    private String id;
    
    @Column(name = "name", nullable = false, length = 255)
    private String name;
    
    // No-arg constructor for JPA
    protected Customer() {}
    
    // Constructor for application use
    public Customer(String id, String name) {
        this.id = id;
        this.name = name;
    }
    
    // Getters (and potentially setters)
    public String getId() { return id; }
    public String getName() { return name; }
}
```

---

## Cross-References

### Related Documentation
- [Program Structure](program-structure.md) - Complete class reference
- [Interfaces](interfaces.md) - Public API contracts
- [JDO Annotations](../specialized/jdo-persistence/annotations.md) - JDO annotation details
- [JDO Persistence Patterns](../specialized/jdo-persistence/persistence-patterns.md) - Persistence usage
- [Technical Debt](../technical-debt/outdated-components.md) - JDO deprecation issues
- [Migration Guide](../migration/component-order.md) - Entity migration strategy

---

*Generated by Comprehensive Codebase Analysis*  
*Last Updated: 2026-01-16*  
*Source: Static analysis of Customer entity*

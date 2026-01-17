# Component Architecture Documentation

## Overview
This document describes all components in the Legacy Java Demo system, their responsibilities, interactions, and architectural roles. Components are organized by module and architectural layer.

---

## Component Inventory

### Total Components: 5
- **Infrastructure Layer**: 2 components (LegacyJdoManager, LegacyQueries)
- **Entity Layer**: 1 component (Customer)
- **Data Access Layer**: 1 component (CustomerDao)
- **Business Logic Layer**: 1 component (CustomerService)

### Module Distribution
- **legacy-wrappers module**: 2 components (infrastructure)
- **legacy-app module**: 3 components (entity, dao, service)

---

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                   Business Logic Layer                   │
│                                                          │
│                    CustomerService                       │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                   Data Access Layer                      │
│                                                          │
│                      CustomerDao                         │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                      Entity Layer                        │
│                                                          │
│                       Customer                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                     │
│                                                          │
│            LegacyJdoManager    LegacyQueries            │
└──────────────────────────────────────────────────────────┘
```

---

## Infrastructure Layer Components

### Component: LegacyJdoManager

#### Identity
- **Name**: LegacyJdoManager
- **Type**: Transaction Management Service
- **Module**: legacy-wrappers
- **Package**: com.verafin.commons.jdo
- **File**: `legacy-wrappers/src/main/java/com/verafin/commons/jdo/LegacyJdoManager.java`

#### Responsibility
Provides transaction lifecycle management for JDO-based data access operations. Acts as a simplified wrapper around JDO transaction APIs.

#### Capabilities
1. **Begin Transaction**: Start new transaction scope
2. **Commit Transaction**: Persist changes to database
3. **Rollback Transaction**: Discard changes on error

#### Public Methods
- `void begin()` - Initialize transaction
- `void commit()` - Commit transaction
- `void rollback()` - Rollback transaction

#### Dependencies
- **Inbound**: CustomerService, CustomerDao (injected via constructor)
- **Outbound**: None (leaf component)

#### Design Patterns
- **Facade Pattern**: Simplifies transaction API
- **Command Pattern**: Transaction operations as commands

#### Architectural Role
- Infrastructure service providing cross-cutting transaction management
- Decouples business logic from persistence transaction details
- Reusable across multiple service/DAO components

#### Usage Example
```java
LegacyJdoManager jdo = new LegacyJdoManager();
jdo.begin();
try {
    // perform operations
    jdo.commit();
} catch (Exception e) {
    jdo.rollback();
    throw e;
}
```

#### Quality Metrics
- **Complexity**: Low (3 simple methods)
- **Coupling**: Low (no dependencies)
- **Cohesion**: High (focused on transaction management)
- **Testability**: High (simple, isolated logic)

#### Technical Debt
- ⚠️ Stub implementation (empty methods)
- ⚠️ No actual JDO integration
- ⚠️ No error handling
- ⚠️ Will be replaced by EntityManager (JPA) or @Transactional (Spring)

---

### Component: LegacyQueries

#### Identity
- **Name**: LegacyQueries
- **Type**: Query Builder Utility
- **Module**: legacy-wrappers
- **Package**: com.verafin.commons.jdo
- **File**: `legacy-wrappers/src/main/java/com/verafin/commons/jdo/LegacyQueries.java`

#### Responsibility
Provides utility methods for constructing JDOQL query strings for common data access patterns.

#### Capabilities
1. **Build Customer ID Query**: Generate JDOQL for customer lookup by ID

#### Public Methods
- `static String byCustomerId(String id)` - Build customer ID query

#### Dependencies
- **Inbound**: CustomerDao
- **Outbound**: None (stateless utility)

#### Design Patterns
- **Utility Class Pattern**: Static methods only
- **Builder Pattern**: Constructs query strings

#### Architectural Role
- Query construction abstraction
- Centralizes query string generation
- Reduces duplication of query logic

#### Usage Example
```java
String query = LegacyQueries.byCustomerId("CUST-001");
// Returns: "SELECT FROM com.verafin.legacy.Customer WHERE id == 'CUST-001'"
```

#### Quality Metrics
- **Complexity**: Low (single method, string concatenation)
- **Coupling**: Low (no dependencies)
- **Cohesion**: Medium (could grow with more query methods)
- **Testability**: High (pure functions)

#### Technical Debt
- 🚨 **CRITICAL**: SQL injection vulnerability (string concatenation)
- ⚠️ No parameterized queries
- ⚠️ Hard-coded entity class names
- ⚠️ Will be replaced by JPQL, Criteria API, or Spring Data Query Methods

#### Security Issue
```java
// Vulnerable code
return "SELECT FROM com.verafin.legacy.Customer WHERE id == '" + id + "'";

// If id = "'; DELETE FROM Customer; --"
// Query becomes: "SELECT FROM ... WHERE id == ''; DELETE FROM Customer; --'"
```

---

## Entity Layer Components

### Component: Customer

#### Identity
- **Name**: Customer
- **Type**: Domain Entity / Value Object
- **Module**: legacy-app
- **Package**: com.verafin.legacy
- **File**: `legacy-app/src/main/java/com/verafin/legacy/Customer.java`

#### Responsibility
Represents customer domain entity with persistent data. Serves as the core domain model for customer information.

#### Capabilities
1. **Store Customer Data**: Hold customer ID and name
2. **Provide Data Access**: Expose customer attributes via getters
3. **Persist Data**: JDO-managed persistence

#### Public Methods
- `Customer(String id, String name)` - Constructor
- `String getId()` - Get customer ID
- `String getName()` - Get customer name

#### Fields
- `String id` - Customer unique identifier (primary key)
- `String name` - Customer name

#### Dependencies
- **Inbound**: CustomerService, CustomerDao (as parameter/return type)
- **Outbound**: javax.jdo.annotations (JDO framework)

#### Design Patterns
- **Value Object Pattern**: Immutable data container
- **Entity Pattern**: Persistent domain object with identity

#### Architectural Role
- Core domain model
- Data transfer object between layers
- Persistence entity

#### Quality Metrics
- **Complexity**: Very Low (simple getters)
- **Coupling**: Very Low (only annotation dependencies)
- **Cohesion**: Very High (single responsibility)
- **Testability**: Very High (simple POJO)
- **Immutability**: Yes (all fields final)

#### Annotations
- `@PersistenceCapable` - JDO entity marker
- `@PrimaryKey` - Primary key designation on id field

#### Technical Debt
- ⚠️ No validation (nulls allowed)
- ⚠️ Immutability may conflict with JDO requirements
- ⚠️ No no-arg constructor (may be required by JDO)
- ⚠️ JDO annotations need migration to JPA

---

## Data Access Layer Components

### Component: CustomerDao

#### Identity
- **Name**: CustomerDao
- **Type**: Data Access Object
- **Module**: legacy-app
- **Package**: com.verafin.legacy
- **File**: `legacy-app/src/main/java/com/verafin/legacy/CustomerDao.java`

#### Responsibility
Encapsulates data access logic for Customer entities. Provides query construction and (conceptually) query execution for customer data retrieval.

#### Capabilities
1. **Build Queries**: Construct JDOQL queries for customer lookup
2. **Abstract Persistence**: Hide JDO query details from business logic

#### Public Methods
- `CustomerDao(LegacyJdoManager jdo)` - Constructor with transaction manager injection
- `String buildFindByIdQuery(String id)` - Build customer ID lookup query

#### Fields
- `LegacyJdoManager jdo` - Transaction manager reference (final)

#### Dependencies
- **Inbound**: CustomerDaoTest
- **Outbound**: LegacyJdoManager (injected), LegacyQueries (static call)

#### Design Patterns
- **Data Access Object (DAO) Pattern**: Encapsulates data access
- **Dependency Injection Pattern**: Constructor injection of transaction manager

#### Architectural Role
- Data access abstraction layer
- Mediates between business logic and persistence
- Query construction responsibility

#### Collaborations
```
CustomerDao
    ├── uses → LegacyJdoManager (for transactions)
    └── uses → LegacyQueries (for query building)
```

#### Usage Example
```java
LegacyJdoManager jdo = new LegacyJdoManager();
CustomerDao dao = new CustomerDao(jdo);
String query = dao.buildFindByIdQuery("CUST-001");
```

#### Quality Metrics
- **Complexity**: Low (simple delegation)
- **Coupling**: Medium (depends on 2 infrastructure components)
- **Cohesion**: High (focused on customer data access)
- **Testability**: High (easy to mock dependencies)

#### Technical Debt
- ⚠️ Incomplete implementation (only query building, no execution)
- ⚠️ Inherits security vulnerability from LegacyQueries
- ⚠️ Transaction manager not actually used (held but not utilized)
- ⚠️ Should be replaced with Spring Data Repository

#### Future Enhancement
```java
// Complete implementation would include:
public Customer findById(String id) {
    jdo.begin();
    try {
        String query = buildFindByIdQuery(id);
        Customer result = executeQuery(query); // Not implemented
        jdo.commit();
        return result;
    } catch (Exception e) {
        jdo.rollback();
        throw e;
    }
}
```

---

## Business Logic Layer Components

### Component: CustomerService

#### Identity
- **Name**: CustomerService
- **Type**: Business Service
- **Module**: legacy-app
- **Package**: com.verafin.legacy
- **File**: `legacy-app/src/main/java/com/verafin/legacy/CustomerService.java`

#### Responsibility
Implements business logic for customer operations. Manages transactions and coordinates customer data formatting with display requirements.

#### Capabilities
1. **Format Customer Display**: Convert customer data to display format
2. **Manage Transactions**: Handle transaction lifecycle for operations
3. **Handle Errors**: Rollback transactions on failures

#### Public Methods
- `CustomerService(LegacyJdoManager jdo)` - Constructor with transaction manager injection
- `String formatDisplay(Customer c)` - Format customer for display with transaction management

#### Fields
- `LegacyJdoManager jdo` - Transaction manager reference (final)

#### Dependencies
- **Inbound**: CustomerServiceTest
- **Outbound**: LegacyJdoManager (injected), Customer (parameter)

#### Design Patterns
- **Service Layer Pattern**: Business logic abstraction
- **Transaction Script Pattern**: Explicit transaction management
- **Dependency Injection Pattern**: Constructor injection

#### Architectural Role
- Business logic coordinator
- Transaction boundary definition
- Application service layer

#### Collaborations
```
CustomerService
    ├── uses → LegacyJdoManager (for transactions)
    └── operates-on → Customer (business entity)
```

#### Usage Example
```java
LegacyJdoManager jdo = new LegacyJdoManager();
CustomerService service = new CustomerService(jdo);
Customer customer = new Customer("1", "Shreya");
String display = service.formatDisplay(customer); // Returns "1:Shreya"
```

#### Business Rules Implemented
1. **Display Format Rule**: Customer display format is `{id}:{name}` with colon separator
2. **Transaction Rule**: All operations must execute within transaction boundaries
3. **Error Recovery Rule**: Rollback transaction on any exception

#### Transaction Flow
```
formatDisplay(Customer c)
    1. BEGIN transaction
    2. Format customer data (id:name)
    3. COMMIT transaction (on success)
    4. ROLLBACK transaction (on exception)
    5. Propagate exception (after rollback)
```

#### Quality Metrics
- **Complexity**: Medium (transaction management + exception handling)
- **Cyclomatic Complexity**: ~3 (try-catch branches)
- **Coupling**: Medium (2 dependencies)
- **Cohesion**: High (focused on customer business logic)
- **Testability**: High (easy to test with mock transaction manager)

#### Technical Debt
- ⚠️ **Design Issue**: Transaction overhead for simple read-only operation
- ⚠️ No actual business logic beyond formatting
- ⚠️ Transaction management should be declarative (e.g., @Transactional)
- ⚠️ Limited functionality (single operation)

#### Modernization Target
```java
// Modern Spring approach
@Service
public class CustomerService {
    @Transactional(readOnly = true)
    public String formatDisplay(Customer c) {
        return c.getId() + ":" + c.getName();
    }
}
```

---

## Component Interaction Matrix

| Component | LegacyJdoManager | LegacyQueries | Customer | CustomerDao | CustomerService |
|-----------|------------------|---------------|----------|-------------|-----------------|
| **LegacyJdoManager** | - | ✗ | ✗ | ← | ← |
| **LegacyQueries** | ✗ | - | ✗ | ← | ✗ |
| **Customer** | ✗ | ✗ | - | ← | ← |
| **CustomerDao** | → | → | → | - | ✗ |
| **CustomerService** | → | ✗ | → | ✗ | - |

Legend:
- `→` Uses/Depends on
- `←` Used by
- `✗` No relationship
- `-` Self

---

## Component Dependencies Graph

```
┌─────────────────┐
│ CustomerService │
└────────┬────────┘
         │ depends on
         ├─────────────┐
         │             │
         ▼             ▼
┌────────────────┐  ┌──────────┐
│LegacyJdoManager│  │ Customer │
└────────────────┘  └──────────┘

┌──────────────┐
│ CustomerDao  │
└──────┬───────┘
       │ depends on
       ├────────────┬──────────────┐
       │            │              │
       ▼            ▼              ▼
┌────────────┐  ┌─────────────┐  ┌──────────┐
│LegacyJdo   │  │LegacyQueries│  │ Customer │
│Manager     │  │             │  │          │
└────────────┘  └─────────────┘  └──────────┘
```

---

## Component Lifecycle

### Instantiation Order
1. **LegacyJdoManager** - No dependencies, created first
2. **Customer** - Entity instantiated as needed
3. **CustomerDao** or **CustomerService** - Injected with LegacyJdoManager
4. **LegacyQueries** - Static utility, no instantiation needed

### Typical Usage Flow
```
1. Application startup
   └── Create LegacyJdoManager instance
   
2. Service initialization
   ├── Create CustomerDao(jdo)
   └── Create CustomerService(jdo)
   
3. Business operation
   ├── CustomerService.formatDisplay(customer)
   │   ├── jdo.begin()
   │   ├── format operation
   │   ├── jdo.commit()
   │   └── return result
   
4. Data access operation
   └── CustomerDao.buildFindByIdQuery(id)
       └── LegacyQueries.byCustomerId(id)
```

---

## Cross-References

### Related Documentation
- [Program Structure](../reference/program-structure.md) - Detailed class documentation
- [Dependencies](dependencies.md) - Dependency analysis
- [System Overview](system-overview.md) - High-level architecture
- [Patterns](patterns.md) - Architectural patterns
- [Business Logic](../behavior/business-logic.md) - Business rule implementation
- [Class Diagram](../diagrams/structural/class-diagram.md) - Visual component relationships

---

*Generated by Comprehensive Codebase Analysis*  
*Last Updated: 2026-01-16*  
*Source: Static analysis of 5 components*

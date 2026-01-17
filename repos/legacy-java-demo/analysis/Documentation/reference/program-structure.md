# Program Structure Reference

## Overview
This document provides a complete structural reference for the Legacy Java Demo codebase, documenting all classes, interfaces, methods, fields, and their relationships across both modules.

## Module Structure

### Module: legacy-wrappers
**Location**: `legacy-wrappers/src/main/java/`  
**Package**: `com.verafin.commons.jdo`  
**Purpose**: JDO infrastructure and utility classes  
**Classes**: 2

### Module: legacy-app
**Location**: `legacy-app/src/main/java/` and `legacy-app/src/test/java/`  
**Package**: `com.verafin.legacy`  
**Purpose**: Customer management application  
**Classes**: 3 (main), 2 (test)  
**Dependencies**: legacy-wrappers

---

## Package: com.verafin.commons.jdo

### Class: LegacyJdoManager
**Type**: Concrete Class  
**File**: `legacy-wrappers/src/main/java/com/verafin/commons/jdo/LegacyJdoManager.java`  
**Purpose**: Provides transaction lifecycle management wrapper for JDO operations  
**Visibility**: public

#### Class Declaration
```java
public class LegacyJdoManager
```

#### Methods

##### begin()
- **Signature**: `public void begin()`
- **Parameters**: None
- **Returns**: void
- **Purpose**: Initiates a new JDO transaction
- **Usage**: Called at the start of transactional operations
- **Implementation**: Empty method body (stub for demonstration)

##### commit()
- **Signature**: `public void commit()`
- **Parameters**: None
- **Returns**: void
- **Purpose**: Commits the current transaction
- **Usage**: Called upon successful completion of transactional operations
- **Implementation**: Empty method body (stub for demonstration)

##### rollback()
- **Signature**: `public void rollback()`
- **Parameters**: None
- **Returns**: void
- **Purpose**: Rolls back the current transaction
- **Usage**: Called when exceptions occur during transactional operations
- **Implementation**: Empty method body (stub for demonstration)

#### Dependencies
- **Outbound**: None
- **Inbound**: CustomerDao, CustomerService (injected via constructor)

#### Relationships
- **Used by**: CustomerDao, CustomerService
- **Inheritance**: Extends Object (implicit)

---

### Class: LegacyQueries
**Type**: Utility Class  
**File**: `legacy-wrappers/src/main/java/com/verafin/commons/jdo/LegacyQueries.java`  
**Purpose**: Provides utility methods for constructing JDO query strings  
**Visibility**: public

#### Class Declaration
```java
public class LegacyQueries
```

#### Methods

##### byCustomerId(String id)
- **Signature**: `public static String byCustomerId(String id)`
- **Parameters**: 
  - `id` (String) - Customer identifier to search for
- **Returns**: String - JDO query string
- **Purpose**: Constructs a JDO query string for finding customers by ID
- **Implementation**: String concatenation to build JDOQL query
- **Query Pattern**: `SELECT FROM com.verafin.legacy.Customer WHERE id == '<id>'`
- **⚠️ Security Issue**: Vulnerable to SQL/JDOQL injection due to direct string concatenation

#### Dependencies
- **Outbound**: None (static utility)
- **Inbound**: CustomerDao

#### Relationships
- **Used by**: CustomerDao
- **Inheritance**: Extends Object (implicit)

---

## Package: com.verafin.legacy

### Class: Customer
**Type**: Entity/Domain Model  
**File**: `legacy-app/src/main/java/com/verafin/legacy/Customer.java`  
**Purpose**: Represents a customer entity with JDO persistence annotations  
**Visibility**: public  
**Persistence**: JDO @PersistenceCapable

#### Class Declaration
```java
@PersistenceCapable
public class Customer
```

#### Annotations
- `@PersistenceCapable` - Marks class as JDO-managed persistent entity
- `@PrimaryKey` - Marks id field as primary key

#### Fields

##### id
- **Type**: String
- **Visibility**: private
- **Modifiers**: final
- **Annotation**: @PrimaryKey
- **Purpose**: Unique identifier for customer
- **Getter**: `public String getId()`

##### name
- **Type**: String
- **Visibility**: private
- **Modifiers**: final
- **Purpose**: Customer name
- **Getter**: `public String getName()`

#### Constructors

##### Customer(String id, String name)
- **Signature**: `public Customer(String id, String name)`
- **Parameters**:
  - `id` (String) - Customer unique identifier
  - `name` (String) - Customer name
- **Purpose**: Creates new Customer instance with specified id and name
- **Implementation**: Initializes final fields

#### Methods

##### getId()
- **Signature**: `public String getId()`
- **Parameters**: None
- **Returns**: String - Customer ID
- **Purpose**: Retrieves customer identifier

##### getName()
- **Signature**: `public String getName()`
- **Parameters**: None
- **Returns**: String - Customer name
- **Purpose**: Retrieves customer name

#### Dependencies
- **Outbound**: javax.jdo.annotations.PersistenceCapable, javax.jdo.annotations.PrimaryKey
- **Inbound**: CustomerService, CustomerDao (conceptually)

#### Relationships
- **Used by**: CustomerService.formatDisplay(), CustomerDao (query target)
- **Inheritance**: Extends Object (implicit)
- **Immutability**: All fields are final (immutable entity)

---

### Class: CustomerDao
**Type**: Data Access Object  
**File**: `legacy-app/src/main/java/com/verafin/legacy/CustomerDao.java`  
**Purpose**: Provides data access methods for Customer entities  
**Visibility**: public

#### Class Declaration
```java
public class CustomerDao
```

#### Fields

##### jdo
- **Type**: LegacyJdoManager
- **Visibility**: private
- **Modifiers**: final
- **Purpose**: Transaction manager for data access operations

#### Constructors

##### CustomerDao(LegacyJdoManager jdo)
- **Signature**: `public CustomerDao(LegacyJdoManager jdo)`
- **Parameters**:
  - `jdo` (LegacyJdoManager) - Transaction manager instance
- **Purpose**: Creates CustomerDao with specified transaction manager
- **Pattern**: Constructor-based dependency injection

#### Methods

##### buildFindByIdQuery(String id)
- **Signature**: `public String buildFindByIdQuery(String id)`
- **Parameters**:
  - `id` (String) - Customer ID to search for
- **Returns**: String - JDO query string
- **Purpose**: Constructs query string for finding customer by ID
- **Implementation**: Delegates to LegacyQueries.byCustomerId()
- **Note**: Query construction only; not executed against database in this demo

#### Dependencies
- **Outbound**: LegacyJdoManager (field), LegacyQueries (method call)
- **Inbound**: CustomerDaoTest

#### Relationships
- **Depends on**: LegacyJdoManager, LegacyQueries
- **Tested by**: CustomerDaoTest
- **Inheritance**: Extends Object (implicit)

---

### Class: CustomerService
**Type**: Service/Business Logic  
**File**: `legacy-app/src/main/java/com/verafin/legacy/CustomerService.java`  
**Purpose**: Provides business logic for customer operations  
**Visibility**: public

#### Class Declaration
```java
public class CustomerService
```

#### Fields

##### jdo
- **Type**: LegacyJdoManager
- **Visibility**: private
- **Modifiers**: final
- **Purpose**: Transaction manager for service operations

#### Constructors

##### CustomerService(LegacyJdoManager jdo)
- **Signature**: `public CustomerService(LegacyJdoManager jdo)`
- **Parameters**:
  - `jdo` (LegacyJdoManager) - Transaction manager instance
- **Purpose**: Creates CustomerService with specified transaction manager
- **Pattern**: Constructor-based dependency injection

#### Methods

##### formatDisplay(Customer c)
- **Signature**: `public String formatDisplay(Customer c)`
- **Parameters**:
  - `c` (Customer) - Customer entity to format
- **Returns**: String - Formatted customer display string
- **Purpose**: Formats customer data for display with transaction management
- **Format**: `{id}:{name}` (e.g., "1:Shreya")
- **Transaction Lifecycle**:
  1. Begins transaction via `jdo.begin()`
  2. Formats customer data as `id:name`
  3. Commits transaction via `jdo.commit()` on success
  4. Rolls back transaction via `jdo.rollback()` on exception
- **Exception Handling**: Catches RuntimeException, rolls back, and re-throws
- **Complexity**: Moderate (transaction management + exception handling)

#### Dependencies
- **Outbound**: LegacyJdoManager (field), Customer (parameter)
- **Inbound**: CustomerServiceTest

#### Relationships
- **Depends on**: LegacyJdoManager, Customer
- **Tested by**: CustomerServiceTest
- **Inheritance**: Extends Object (implicit)

---

## Test Classes

### Class: CustomerDaoTest
**Type**: Test Class  
**File**: `legacy-app/src/test/java/com/verafin/legacy/CustomerDaoTest.java`  
**Framework**: JUnit 5 (Jupiter)  
**Purpose**: Unit tests for CustomerDao

#### Test Methods

##### buildsLegacyQuery()
- **Annotation**: @Test
- **Purpose**: Verifies that CustomerDao correctly builds JDO query strings
- **Test Steps**:
  1. Creates CustomerDao with new LegacyJdoManager
  2. Calls buildFindByIdQuery("123")
  3. Asserts query contains "Customer"
  4. Asserts query contains "id =="
- **Dependencies**: JUnit 5 assertions

---

### Class: CustomerServiceTest
**Type**: Test Class  
**File**: `legacy-app/src/test/java/com/verafin/legacy/CustomerServiceTest.java`  
**Framework**: JUnit 5 (Jupiter)  
**Purpose**: Unit tests for CustomerService

#### Test Methods

##### formatsDisplay()
- **Annotation**: @Test
- **Purpose**: Verifies that CustomerService correctly formats customer display
- **Test Steps**:
  1. Creates CustomerService with new LegacyJdoManager
  2. Creates test Customer("1", "Shreya")
  3. Calls formatDisplay() on customer
  4. Asserts result equals "1:Shreya"
- **Dependencies**: JUnit 5 assertions

---

## Inheritance Hierarchy

### Root: Object (java.lang)
All classes implicitly extend Object:
- LegacyJdoManager
- LegacyQueries
- Customer
- CustomerDao
- CustomerService
- CustomerDaoTest
- CustomerServiceTest

### No Explicit Inheritance
No classes in this codebase use explicit inheritance (no `extends` clauses beyond implicit Object).

---

## Composition Relationships

### LegacyJdoManager Composition
```
CustomerDao
    └── has-a: LegacyJdoManager (injected)

CustomerService
    └── has-a: LegacyJdoManager (injected)
```

### Customer Usage
```
CustomerService
    └── operates-on: Customer (method parameter)
```

### Query Utility Usage
```
CustomerDao
    └── uses: LegacyQueries.byCustomerId() (static method)
```

---

## Dependency Graph

### Module Dependencies
```
legacy-app
    └── depends-on: legacy-wrappers
```

### Class Dependencies (Outbound)
```
Customer
    └── javax.jdo.annotations.*

CustomerDao
    ├── LegacyJdoManager
    └── LegacyQueries

CustomerService
    ├── LegacyJdoManager
    └── Customer

LegacyJdoManager
    └── (none)

LegacyQueries
    └── (none)
```

### Class Dependencies (Inbound - Usage)
```
LegacyJdoManager
    ├── used-by: CustomerDao
    └── used-by: CustomerService

LegacyQueries
    └── used-by: CustomerDao

Customer
    └── used-by: CustomerService
```

---

## Method Summary

### Total Method Count: 11

#### By Class
- LegacyJdoManager: 3 methods
- LegacyQueries: 1 static method
- Customer: 3 methods (1 constructor, 2 getters)
- CustomerDao: 2 methods (1 constructor, 1 business method)
- CustomerService: 2 methods (1 constructor, 1 business method)

#### By Visibility
- Public: 11 methods (100%)
- Protected: 0 methods
- Package-private: 0 methods
- Private: 0 methods

#### By Type
- Constructors: 3
- Static methods: 1
- Instance methods: 7

---

## Field Summary

### Total Field Count: 5

#### By Class
- Customer: 2 fields (id, name)
- CustomerDao: 1 field (jdo)
- CustomerService: 1 field (jdo)
- LegacyJdoManager: 0 fields
- LegacyQueries: 0 fields

#### By Visibility
- Private: 5 fields (100%)
- Public: 0 fields

#### By Modifiers
- Final: 5 fields (100%)
- Non-final: 0 fields

---

## Annotation Usage

### JDO Annotations
- `@PersistenceCapable`: 1 usage (Customer class)
- `@PrimaryKey`: 1 usage (Customer.id field)

### Test Annotations
- `@Test`: 2 usages (CustomerDaoTest.buildsLegacyQuery, CustomerServiceTest.formatsDisplay)

---

## Cross-References

### Related Documentation
- [Data Models](data-models.md) - Detailed Customer entity documentation
- [Interfaces](interfaces.md) - Public API contracts
- [Component Architecture](../architecture/components.md) - Component responsibilities
- [Dependencies](../architecture/dependencies.md) - Dependency analysis
- [JDO Persistence Patterns](../specialized/jdo-persistence/persistence-patterns.md) - JDO usage patterns
- [Business Logic](../behavior/business-logic.md) - Business rule implementation
- [Class Diagram](../diagrams/structural/class-diagram.md) - Visual representation

---

*Generated by Comprehensive Codebase Analysis*  
*Last Updated: 2026-01-16*  
*Source: Static analysis of 7 Java files*

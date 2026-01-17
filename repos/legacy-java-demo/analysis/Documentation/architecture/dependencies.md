# Dependency Analysis

## Overview
This document provides comprehensive analysis of all dependencies in the Legacy Java Demo codebase, including internal module dependencies, class dependencies, and external library dependencies.

---

## Dependency Summary

### Module Dependencies
- **Total Modules**: 2
- **Internal Dependencies**: 1 (legacy-app → legacy-wrappers)
- **External Dependencies**: 2 (JDO API, JUnit 5)

### Class Dependencies
- **Total Classes**: 5 (excluding tests)
- **Maximum Dependency Depth**: 2 levels
- **Circular Dependencies**: 0

---

## Module Dependency Analysis

### Module Dependency Graph

```
┌────────────────┐
│  legacy-app    │
│  (module)      │
└───────┬────────┘
        │
        │ depends on
        │ (project reference)
        ▼
┌────────────────┐
│legacy-wrappers │
│  (module)      │
└────────────────┘
```

### Module: legacy-wrappers

**Role**: Foundation/Infrastructure Module  
**Dependencies**: None (leaf module)  
**Dependents**: legacy-app

#### Provides
- Transaction management infrastructure (LegacyJdoManager)
- Query building utilities (LegacyQueries)

#### build.gradle
```gradle
dependencies {
    // intentionally empty (wrapper module)
}
```

**Characteristics**:
- Zero external dependencies
- Self-contained infrastructure
- Reusable across projects
- No runtime dependencies beyond JDK

---

### Module: legacy-app

**Role**: Application Module  
**Dependencies**: legacy-wrappers, javax.jdo:jdo-api:3.1  
**Dependents**: None (top-level module)

#### Consumes
- LegacyJdoManager (from legacy-wrappers)
- LegacyQueries (from legacy-wrappers)

#### Provides
- Customer entity
- CustomerDao
- CustomerService

#### build.gradle
```gradle
dependencies {
    implementation project(":legacy-wrappers")
    implementation "javax.jdo:jdo-api:3.1"
}
```

**Characteristics**:
- Depends on wrapper module for infrastructure
- Depends on JDO API for persistence annotations
- Application-level module (not reusable)

---

## Internal Class Dependencies

### Dependency Layers

```
Layer 4: Business Logic
    ┌──────────────────┐
    │ CustomerService  │
    └────────┬─────────┘
             │
Layer 3: Data Access
    ┌────────┴─────────┐
    │   CustomerDao    │
    └────────┬─────────┘
             │
Layer 2: Entity
    ┌────────┴─────────┐
    │    Customer      │
    └──────────────────┘

Layer 1: Infrastructure (legacy-wrappers)
    ┌──────────────────┐      ┌──────────────────┐
    │LegacyJdoManager  │      │ LegacyQueries    │
    └──────────────────┘      └──────────────────┘
```

---

### Detailed Class Dependencies

#### LegacyJdoManager
**Outbound Dependencies**: None  
**Inbound Dependencies**: CustomerDao, CustomerService  
**Dependency Type**: Injected (constructor)  
**Dependency Level**: 0 (leaf component)

```
LegacyJdoManager (no dependencies)
```

---

#### LegacyQueries
**Outbound Dependencies**: None  
**Inbound Dependencies**: CustomerDao  
**Dependency Type**: Static method call  
**Dependency Level**: 0 (leaf component)

```
LegacyQueries (no dependencies)
```

---

#### Customer
**Outbound Dependencies**: javax.jdo.annotations.*  
**Inbound Dependencies**: CustomerService, CustomerDao  
**Dependency Type**: Parameter/Return type  
**Dependency Level**: 1

```
Customer
    └── javax.jdo.annotations.PersistenceCapable
    └── javax.jdo.annotations.PrimaryKey
```

---

#### CustomerDao
**Outbound Dependencies**: LegacyJdoManager, LegacyQueries, Customer (indirectly)  
**Inbound Dependencies**: CustomerDaoTest  
**Dependency Type**: Field injection, static method call  
**Dependency Level**: 2

```
CustomerDao
    ├── LegacyJdoManager (constructor injection)
    └── LegacyQueries (static method call)
        └── (implicitly references Customer entity in query)
```

**Dependency Injection Pattern**:
```java
private final LegacyJdoManager jdo;

public CustomerDao(LegacyJdoManager jdo) {
    this.jdo = jdo;
}
```

---

#### CustomerService
**Outbound Dependencies**: LegacyJdoManager, Customer  
**Inbound Dependencies**: CustomerServiceTest  
**Dependency Type**: Field injection, method parameter  
**Dependency Level**: 2

```
CustomerService
    ├── LegacyJdoManager (constructor injection)
    └── Customer (method parameter)
```

**Dependency Injection Pattern**:
```java
private final LegacyJdoManager jdo;

public CustomerService(LegacyJdoManager jdo) {
    this.jdo = jdo;
}
```

---

## Dependency Matrix

### Compile-Time Dependencies

|                    | LegacyJdoManager | LegacyQueries | Customer | CustomerDao | CustomerService |
|--------------------|------------------|---------------|----------|-------------|-----------------|
| **LegacyJdoManager** | -              | No            | No       | No          | No              |
| **LegacyQueries**    | No             | -             | No       | No          | No              |
| **Customer**         | No             | No            | -        | No          | No              |
| **CustomerDao**      | **Yes**        | **Yes**       | Indirect | -           | No              |
| **CustomerService**  | **Yes**        | No            | **Yes**  | No          | -               |

### Runtime Dependencies

|                    | LegacyJdoManager | LegacyQueries | Customer | CustomerDao | CustomerService |
|--------------------|------------------|---------------|----------|-------------|-----------------|
| **CustomerDao**      | **Required**   | **Required**  | Optional | -           | No              |
| **CustomerService**  | **Required**   | No            | **Required** | No      | -               |

---

## External Dependencies

### Runtime Dependencies

#### javax.jdo:jdo-api:3.1
**Type**: Compile + Runtime  
**Scope**: implementation  
**Purpose**: JDO persistence framework API  
**Used By**: Customer entity (annotations)  
**Module**: legacy-app only

**Provides**:
- `@PersistenceCapable` annotation
- `@PrimaryKey` annotation
- JDO query APIs (not directly used in this demo)

**Dependency Details**:
```gradle
implementation "javax.jdo:jdo-api:3.1"
```

**Maven Coordinates**:
```xml
<dependency>
    <groupId>javax.jdo</groupId>
    <artifactId>jdo-api</artifactId>
    <version>3.1</version>
</dependency>
```

**Technical Debt**:
- ⚠️ **Obsolete Framework**: JDO largely replaced by JPA
- ⚠️ **Old Namespace**: Uses `javax.*` (pre-Jakarta EE)
- ⚠️ **Version**: 3.1 released 2013 (11+ years old)
- ⚠️ **Maintenance**: Limited community support

**Migration Path**:
```gradle
// Replace with:
implementation "jakarta.persistence:jakarta.persistence-api:3.1.0"
```

---

### Test Dependencies

#### org.junit.jupiter:junit-jupiter:5.10.2
**Type**: Test Only  
**Scope**: testImplementation  
**Purpose**: Unit testing framework  
**Used By**: CustomerDaoTest, CustomerServiceTest  
**Module**: All subprojects (defined in root build.gradle)

**Provides**:
- JUnit 5 test annotations (`@Test`)
- Assertion methods (`assertTrue`, `assertEquals`)
- Test runner infrastructure

**Dependency Details**:
```gradle
testImplementation "org.junit.jupiter:junit-jupiter:5.10.2"
```

**Characteristics**:
- ✅ Modern version (released 2024)
- ✅ Active development
- ✅ Industry standard

---

## Dependency Graph Visualization

### Complete Dependency Graph

```
┌─────────────────────────────────────────────────────────┐
│                      Application                         │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
┌───────────────────┐             ┌─────────────────┐
│  CustomerService  │             │  CustomerDao    │
└─────────┬─────────┘             └────────┬────────┘
          │                                │
          │ uses                           │ uses
          ├────────────────────────────────┤
          │                                │
          ▼                                ▼
┌─────────────────────┐         ┌──────────────────┐
│ LegacyJdoManager    │         │ LegacyQueries    │
└─────────────────────┘         └──────────────────┘
          ▲                                ▲
          │                                │
          │ from legacy-wrappers module    │
          └────────────────────────────────┘

┌─────────────────────┐
│     Customer        │
│   (JDO Entity)      │
└──────────┬──────────┘
           │
           │ depends on
           ▼
┌─────────────────────┐
│  javax.jdo:jdo-api  │
│     (external)      │
└─────────────────────┘
```

---

## Dependency Characteristics

### Coupling Analysis

#### Low Coupling (Good)
- **LegacyJdoManager**: 0 outbound dependencies
- **LegacyQueries**: 0 outbound dependencies (except JDK)
- **Customer**: 1 external dependency (JDO annotations only)

#### Medium Coupling (Acceptable)
- **CustomerDao**: 2 dependencies (both from same module)
- **CustomerService**: 2 dependencies (1 infrastructure, 1 entity)

#### High Coupling (None)
No components exhibit high coupling.

---

### Cohesion Analysis

#### High Cohesion (Good)
- **LegacyJdoManager**: Transaction management only
- **LegacyQueries**: Query building only
- **Customer**: Data representation only
- **CustomerDao**: Data access only
- **CustomerService**: Business logic only

---

### Dependency Stability

#### Stable Dependencies (No Dependencies)
- LegacyJdoManager
- LegacyQueries

#### Abstract Dependencies (Entity)
- Customer (abstract data representation)

#### Unstable Dependencies (Multiple Dependencies)
- CustomerDao (depends on 2 components)
- CustomerService (depends on 2 components)

**Stability Metrics**:
- **Abstractness**: Low (no interfaces)
- **Instability**: Low to Medium (most components have 0-2 dependencies)

---

## Dependency Injection Analysis

### Injection Patterns Used

#### Constructor Injection (Preferred)
```java
// Pattern used in CustomerDao and CustomerService
public class Component {
    private final Dependency dep;
    
    public Component(Dependency dep) {
        this.dep = dep;
    }
}
```

**Advantages**:
- Explicit dependencies
- Immutable dependency references (final)
- Easy to test (mock injection)
- No hidden dependencies

**Used By**:
- CustomerDao (injects LegacyJdoManager)
- CustomerService (injects LegacyJdoManager)

#### Static Method Call (Utility)
```java
// Pattern used in CustomerDao
String query = LegacyQueries.byCustomerId(id);
```

**Characteristics**:
- No instance required
- Stateless operation
- Tight coupling to utility class

**Used By**:
- CustomerDao → LegacyQueries

---

## Transitive Dependencies

### Direct vs Transitive

#### legacy-app Direct Dependencies
```
legacy-app
├── legacy-wrappers (project)
└── javax.jdo:jdo-api:3.1
```

#### legacy-app Transitive Dependencies
```
(none - jdo-api has no transitive dependencies)
```

### Dependency Tree
```
legacy-app
├── javax.jdo:jdo-api:3.1
│   └── (no transitive dependencies)
└── project :legacy-wrappers
    └── (no dependencies)
```

---

## Dependency Risk Assessment

### Critical Dependencies

#### javax.jdo:jdo-api:3.1
- **Risk Level**: 🔴 **HIGH**
- **Issues**:
  - Obsolete framework
  - Limited maintenance
  - Pre-Jakarta namespace
  - Blocks modernization
- **Impact**: Core persistence dependency
- **Mitigation**: Migrate to JPA

#### legacy-wrappers (Internal)
- **Risk Level**: 🟡 **MEDIUM**
- **Issues**:
  - Stub implementation
  - No actual functionality
  - Will need replacement
- **Impact**: Transaction management
- **Mitigation**: Replace with Spring @Transactional or EntityManager

---

## Dependency Cycles

### Cycle Detection Result
✅ **No circular dependencies detected**

All dependencies form a directed acyclic graph (DAG).

---

## Dependency Upgrade Path

### Phase 1: Update Test Dependencies
```gradle
// Already on latest version
testImplementation "org.junit.jupiter:junit-jupiter:5.10.2" ✅
```

### Phase 2: Migrate JDO to JPA
```gradle
// Remove
implementation "javax.jdo:jdo-api:3.1" ❌

// Add
implementation "jakarta.persistence:jakarta.persistence-api:3.1.0" ✅
implementation "org.springframework.boot:spring-boot-starter-data-jpa:3.2.0" ✅
```

### Phase 3: Refactor Infrastructure
```java
// Remove legacy-wrappers dependency
// Replace with Spring framework components
@Service
@Transactional
public class CustomerService { ... }
```

---

## Dependency Management Recommendations

### Immediate Actions
1. ✅ Document JDO deprecation in technical debt
2. ⚠️ Plan JPA migration
3. ⚠️ Audit security vulnerabilities in LegacyQueries

### Short Term (3-6 months)
1. Migrate from JDO to JPA
2. Replace LegacyJdoManager with Spring @Transactional
3. Implement parameterized queries

### Long Term (6-12 months)
1. Adopt Spring Data JPA repositories
2. Remove legacy-wrappers module
3. Implement reactive persistence (if needed)

---

## Cross-References

### Related Documentation
- [Components](components.md) - Component architecture and responsibilities
- [Technical Debt Report](../technical-debt-report.md) - Dependency-related technical debt
- [Outdated Components](../technical-debt/outdated-components.md) - JDO deprecation details
- [Security Vulnerabilities](../technical-debt/security-vulnerabilities.md) - Dependency security issues
- [Migration Guide](../migration/component-order.md) - Dependency migration order
- [Remediation Plan](../technical-debt/remediation-plan.md) - Dependency upgrade strategy

---

*Generated by Comprehensive Codebase Analysis*  
*Last Updated: 2026-01-16*  
*Source: Static analysis of build.gradle files and Java imports*

# Dependency Analysis

**Generated from:** Static code analysis of transform-jdo-demo  
**Analysis Date:** 2026-01-18

## Table of Contents
1. [Overview](#overview)
2. [External Dependencies](#external-dependencies)
3. [Internal Component Dependencies](#internal-component-dependencies)
4. [Dependency Graph](#dependency-graph)
5. [Criticality Analysis](#criticality-analysis)

---

## Overview

The codebase has a **simple dependency structure** with:
- **4 external library dependencies**
- **6 internal component relationships**
- **2-3 layer depth** in dependency chains
- **No circular dependencies** detected

---

## External Dependencies

### Production Dependencies

#### 1. javax.jdo:jdo-api:3.1

**Type:** Legacy Persistence API  
**Scope:** Production (implementation)  
**Declared in:** `legacy-app/build.gradle`  
**Release Date:** 2013  
**Status:** ⚠️ **DEPRECATED** - No active development

**Usage in Codebase:**
- Referenced by: JdoPropertyKeys (property key names)
- Pattern: Uses JDO naming conventions for configuration
- Actual JDO classes: **NOT DIRECTLY USED** (only conventions followed)

**Purpose:** Provides standard property keys for JDBC configuration:
- `javax.jdo.option.ConnectionUserName`
- `javax.jdo.option.ConnectionPassword`
- `javax.jdo.option.ConnectionURL`

**Risk Level:** 🔴 **CRITICAL**
- Obsolete technology with no modern support
- No security patches or updates
- Limited community knowledge

**Migration Path:** Migrate to JPA 3.x or Spring Data JPA

---

#### 2. com.google.guava:guava:33.0.0-jre

**Type:** Utility Library  
**Scope:** Production (implementation)  
**Declared in:** `legacy-app/build.gradle`  
**Release Date:** January 2024  
**Status:** ✅ Active, well-maintained

**Usage in Codebase:**
- **DECLARED BUT NOT USED** - No imports found in source code
- Likely added for utility functions but currently unused

**Purpose (If Used):** Collections utilities, caching, primitives support

**Risk Level:** 🟢 **LOW**
- Modern version, actively maintained
- Well-tested library from Google
- Zero actual usage means can be removed

**Recommendation:** Remove dependency if truly unused to reduce dependency footprint

---

### Test Dependencies

#### 3. org.junit.jupiter:junit-jupiter:5.10.2

**Type:** Testing Framework  
**Scope:** Test (testImplementation)  
**Declared in:** `build.gradle` (subprojects block)  
**Release Date:** February 2024  
**Status:** ✅ Active, latest JUnit 5.x version

**Usage in Codebase:**
- UserServiceTest (1 test class)
- Imports: `org.junit.jupiter.api.Test`, `org.junit.jupiter.api.Assertions`
- 1 test method: `changeEmail_returnsTrue_forExistingUser()`

**Purpose:** Unit testing framework with modern annotations and assertions

**Risk Level:** 🟢 **LOW**
- Modern, stable version
- Standard Java testing framework
- Minimal test coverage (1 test) is the risk, not the library

**Coverage Impact:** Only 1 test for entire 8-class production codebase (~11% class coverage)

---

#### 4. org.mockito:mockito-core:5.8.0

**Type:** Mocking Framework  
**Scope:** Test (testImplementation)  
**Declared in:** `build.gradle` (subprojects block)  
**Release Date:** November 2023  
**Status:** ✅ Active, recent version

**Usage in Codebase:**
- **IMPORTED BUT NOT USED** - UserServiceTest imports but doesn't use mocks
- No mocking operations in the single test

**Purpose (If Used):** Mock object creation for isolated unit testing

**Risk Level:** 🟢 **LOW**
- Modern version, actively maintained
- Currently unused in tests (test uses real LegacyJdoManager)

**Recommendation:** Either use for proper unit testing or remove to reduce dependencies

---

## Internal Component Dependencies

### Component Relationship Matrix

| Component | Depends On | Used By | Dependency Type |
|-----------|------------|---------|-----------------|
| **LegacyJdoManager** | None | UserDao, UserService, BillingService | Core Infrastructure |
| **LegacyQueries** | None | UserDao, BillingService | Utility |
| **JdoPropertyKeys** | None | LegacyDbConfig | Constants |
| **LegacyDbConfig** | JdoPropertyKeys | (External configuration consumers) | Configuration |
| **UserRecord** | None | UserDao | Data Model |
| **UserDao** | LegacyJdoManager, LegacyQueries | UserService | Data Access |
| **UserService** | LegacyJdoManager, UserDao | (Application/API layer) | Business Logic |
| **BillingService** | LegacyJdoManager, LegacyQueries | (Application/API layer) | Business Logic |

---

### Dependency Chains

#### Chain 1: User Management Flow
```
UserService
    ├─→ LegacyJdoManager (transaction management)
    └─→ UserDao
         ├─→ LegacyJdoManager (query execution)
         └─→ LegacyQueries (SQL definitions)
```
**Depth:** 3 levels  
**Components:** 4

---

#### Chain 2: Billing Flow
```
BillingService
    ├─→ LegacyJdoManager (transaction + query execution)
    └─→ LegacyQueries (SQL definitions)
```
**Depth:** 2 levels  
**Components:** 3

---

#### Chain 3: Configuration Flow
```
LegacyDbConfig
    └─→ JdoPropertyKeys (property key constants)
```
**Depth:** 2 levels  
**Components:** 2

---

## Dependency Graph

### Visual Representation (Text-Based)

```
┌─────────────────────┐
│   UserService       │ (Business Logic)
└──────┬──────┬───────┘
       │      │
       │      └────────────┐
       ↓                   ↓
┌─────────────────┐   ┌─────────────────┐
│    UserDao      │   │ LegacyJdoManager│ (Core)
└──────┬──────────┘   └────────┬────────┘
       │                       ↑
       │                       │
       ↓                       │
┌─────────────────┐            │
│ LegacyQueries   │←───────────┤
└─────────────────┘            │
                               │
┌─────────────────────┐        │
│  BillingService     │ (Business Logic)
└──────────┬──────────┘        │
           │                   │
           └───────────────────┘

┌─────────────────────┐
│  LegacyDbConfig     │ (Configuration)
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  JdoPropertyKeys    │ (Constants)
└─────────────────────┘

┌─────────────────────┐
│    UserRecord       │ (Data Model - Independent)
└─────────────────────┘
```

---

## Criticality Analysis

### Critical Path Components

Components ranked by **dependency impact** (how many components depend on them):

#### 1. LegacyJdoManager - 🔴 CRITICAL
**Depended on by:** 3 components (UserDao, UserService, BillingService)  
**Impact if changed:** Breaks entire persistence layer  
**Risk:** High - Single point of failure for all database operations

**Characteristics:**
- Core infrastructure component
- Provides transaction management
- All data access flows through it
- Stateful design (ConcurrentHashMap) increases complexity

**Migration Priority:** HIGH - Must be first component modernized

---

#### 2. LegacyQueries - 🟡 MEDIUM
**Depended on by:** 2 components (UserDao, BillingService)  
**Impact if changed:** Breaks database query execution  
**Risk:** Medium - Changes affect multiple services

**Characteristics:**
- Centralized SQL definition
- Immutable (final class, static methods)
- Easy to test in isolation
- Good separation of concerns

**Migration Priority:** MEDIUM - Can be updated independently

---

#### 3. UserDao - 🟢 LOW
**Depended on by:** 1 component (UserService)  
**Impact if changed:** Breaks user service only  
**Risk:** Low - Limited blast radius

**Characteristics:**
- Well-encapsulated data access
- Clear single responsibility
- Good candidate for replacement

**Migration Priority:** LOW - Can be last in user management chain

---

#### 4. JdoPropertyKeys - 🟢 LOW
**Depended on by:** 1 component (LegacyDbConfig)  
**Impact if changed:** Breaks configuration loading  
**Risk:** Low - Easy to replace

**Characteristics:**
- Simple constants definition
- No logic
- Configuration-only component

**Migration Priority:** LOW - Simple to modernize

---

### Independent Components (No Dependencies)

These can be modified/tested in isolation:

1. **UserRecord** - Pure data model, no dependencies
2. **LegacyQueries** - Only string constants
3. **JdoPropertyKeys** - Only string constants
4. **LegacyJdoManager** - Only uses Java standard library

---

## Package-Level Dependencies

### Package Dependency Graph

```
com.transformtest.legacy.user
    ├─→ com.transformtest.legacy.jdo (3 references)
    └─→ java.util.*

com.transformtest.legacy.billing
    ├─→ com.transformtest.legacy.jdo (2 references)
    ├─→ java.util.*
    └─→ java.math.BigDecimal

com.transformtest.legacy.jdo
    └─→ java.util.* (Map, List, HashMap, ConcurrentHashMap)

com.acme.legacy.config ⚠️ DIFFERENT ROOT
    └─→ com.acme.legacy.jdo (should be com.transformtest.legacy.jdo)
```

**Issue:** Package name inconsistency indicates partial refactoring or organizational debt

---

## Dependency Health Assessment

### External Dependency Health

| Dependency | Version | Age | Security | Maintenance | Health Score |
|------------|---------|-----|----------|-------------|--------------|
| javax.jdo:jdo-api | 3.1 | 11 years | ⚠️ No updates | 🔴 Abandoned | 🔴 POOR |
| guava | 33.0.0-jre | Current | ✅ Active | ✅ Google | ✅ EXCELLENT |
| junit-jupiter | 5.10.2 | Current | ✅ Active | ✅ Community | ✅ EXCELLENT |
| mockito-core | 5.8.0 | Recent | ✅ Active | ✅ Community | ✅ EXCELLENT |

**Overall Health:** 🟡 **MIXED**
- 3/4 dependencies are healthy
- 1/4 is critical technical debt (JDO)

---

## Dependency Risks

### Risk Matrix

| Risk Type | Severity | Affected Dependency | Impact |
|-----------|----------|---------------------|--------|
| **Obsolete Technology** | 🔴 CRITICAL | javax.jdo:jdo-api:3.1 | No security patches, no community support |
| **Unused Dependencies** | 🟡 MEDIUM | guava:33.0.0-jre | Unnecessary attack surface |
| **Unused Test Tools** | 🟢 LOW | mockito-core:5.8.0 | Minimal impact, easy to use or remove |
| **Package Inconsistency** | 🟡 MEDIUM | com.acme vs com.transformtest | Maintenance confusion |

---

## Migration Impact Analysis

### Scenario: Replace JDO with JPA

**Components Requiring Changes:**

1. **Direct Impact (Must Change):**
   - LegacyJdoManager → JPAManager or EntityManager
   - JdoPropertyKeys → JPA property keys
   - LegacyDbConfig → JPA DataSource configuration

2. **Indirect Impact (May Need Updates):**
   - UserDao → Use JPA EntityManager APIs
   - BillingService → Use JPA transactions
   - UserService → Use JPA transactions
   - UserRecord → Add JPA @Entity annotations

3. **No Impact (Can Remain):**
   - LegacyQueries → Can keep SQL (JPQL optional)
   - Test classes → Update mocks only

**Estimated Effort:** 
- Small codebase: 2-3 days
- Well-structured: Clear separation aids migration
- Risk: Medium (transaction semantics must match)

---

## Dependency Isolation

### Components with Good Isolation

✅ **UserRecord** - Zero dependencies, pure data  
✅ **LegacyQueries** - Only strings, no external dependencies  
✅ **JdoPropertyKeys** - Only strings, no external dependencies

### Components with Poor Isolation

❌ **LegacyJdoManager** - Used by 3 components, hard to replace  
❌ **UserService** - Tightly coupled to UserDao AND LegacyJdoManager  
❌ **BillingService** - Direct dependency on LegacyJdoManager (bypasses DAO layer)

---

## Recommendations

### Immediate Actions

1. **Remove Unused Dependencies:**
   - Consider removing Guava if truly unused
   - Use Mockito in tests or remove it

2. **Fix Package Inconsistency:**
   - Standardize on one package root (com.transformtest.legacy)
   - Update LegacyDbConfig package

3. **Add Dependency Management:**
   - Add dependency version management (BOM)
   - Document why each dependency exists

### Short-Term Actions

4. **Increase Test Coverage:**
   - Currently 1 test with 2 dependencies (JUnit, Mockito)
   - Add tests for all critical paths

5. **Document Dependencies:**
   - Add comments explaining JDO dependency purpose
   - Document migration plan

### Long-Term Actions

6. **Migrate from JDO:**
   - Replace javax.jdo with JPA 3.x
   - Or use Spring Data JPA for modern patterns
   - Estimated effort: 2-3 days for this codebase

---

## Related Documentation

- [Program Structure](../reference/program-structure.md)
- [Technical Debt - Outdated Components](../technical-debt/outdated-components.md)
- [Architecture Dependencies](../architecture/dependencies.md)
- [Migration Component Order](../migration/component-order.md)

---

*Dependency analysis performed through static code inspection and build file analysis.*

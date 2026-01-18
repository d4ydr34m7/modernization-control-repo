# Architecture Dependencies

**Project:** transform-jdo-demo  
**Generated:** 2026-01-18

## Table of Contents
1. [Dependency Overview](#dependency-overview)
2. [External Dependencies](#external-dependencies)
3. [Internal Component Dependencies](#internal-component-dependencies)
4. [Transitive Dependencies](#transitive-dependencies)
5. [Dependency Management](#dependency-management)

---

## Dependency Overview

The system has a **minimal external dependency footprint** with:
- **4 external library dependencies** (2 production, 2 test)
- **6 internal component relationships**
- **2-tier maximum dependency depth**

### Dependency Philosophy
- **Minimal externals:** Only essential libraries
- **Direct dependencies:** No complex transitive chains
- **Legacy approach:** Using older, stable (but deprecated) technologies

---

## External Dependencies

### Production Dependencies

#### 1. javax.jdo:jdo-api:3.1

**Category:** Persistence API  
**Scope:** implementation  
**Declared:** `legacy-app/build.gradle`

**Coordinates:**
```gradle
implementation "javax.jdo:jdo-api:3.1"
```

**Purpose:**
- Provides JDO (Java Data Objects) API specification
- Used for property key naming conventions
- NOT directly used for actual JDO operations (only conventions followed)

**Version Details:**
- **Released:** 2013
- **Status:** 🔴 **DEPRECATED** / Abandoned
- **Last Update:** Over 11 years ago
- **Active Development:** ❌ None
- **Security Patches:** ❌ None

**Usage in Codebase:**
- JdoPropertyKeys references standard property names:
  - `javax.jdo.option.ConnectionUserName`
  - `javax.jdo.option.ConnectionPassword`
  - `javax.jdo.option.ConnectionURL`
- No actual JDO classes imported or used

**Risk Assessment:** 🔴 **CRITICAL**
- Obsolete technology with no support
- No community knowledge base
- No bug fixes or security updates
- Blocks modern JVM features

**Migration Path:**
- Replace with JPA (Jakarta Persistence) 3.x
- Or use Spring Data JPA for modern patterns
- Estimated effort: 2-3 days for this codebase

---

#### 2. com.google.guava:guava:33.0.0-jre

**Category:** Utility Library  
**Scope:** implementation  
**Declared:** `legacy-app/build.gradle`

**Coordinates:**
```gradle
implementation "com.google.guava:guava:33.0.0-jre"
```

**Purpose:**
- General-purpose utilities (collections, caching, primitives, etc.)
- **DECLARED BUT NOT USED** in current codebase

**Version Details:**
- **Released:** January 2024
- **Status:** ✅ Active, well-maintained
- **Maintainer:** Google
- **JDK Compatibility:** Java 8+

**Usage in Codebase:**
- ❌ **ZERO usage** - No imports found
- Likely added for anticipated needs but never utilized

**Risk Assessment:** 🟢 **LOW**
- Modern, actively maintained
- Well-tested and stable
- Currently unused means can be safely removed

**Recommendation:**
- **Remove** if truly unused to reduce attack surface
- Or document intended usage

**Size Impact:** ~2.8 MB JAR (unused bloat)

---

### Test Dependencies

#### 3. org.junit.jupiter:junit-jupiter:5.10.2

**Category:** Testing Framework  
**Scope:** testImplementation  
**Declared:** `build.gradle` (subprojects block)

**Coordinates:**
```gradle
testImplementation "org.junit.jupiter:junit-jupiter:5.10.2"
```

**Purpose:**
- JUnit 5 testing framework
- Modern annotation-based testing
- Used for unit testing

**Version Details:**
- **Released:** February 2024
- **Status:** ✅ Active (latest 5.x series)
- **Maintainer:** JUnit Team
- **JDK Compatibility:** Java 8+

**Usage in Codebase:**
- UserServiceTest uses JUnit 5 annotations
- Imports: `org.junit.jupiter.api.Test`, `org.junit.jupiter.api.Assertions`
- 1 test class, 1 test method

**Risk Assessment:** 🟢 **LOW**
- Modern, stable version
- Standard Java testing framework
- Well-maintained and supported

**Coverage Impact:**
- Only 1 test for 8 production classes
- Test coverage is the issue, not the framework

---

#### 4. org.mockito:mockito-core:5.8.0

**Category:** Mocking Framework  
**Scope:** testImplementation  
**Declared:** `build.gradle` (subprojects block)

**Coordinates:**
```gradle
testImplementation "org.mockito:mockito-core:5.8.0"
```

**Purpose:**
- Mock object creation for isolated unit testing
- Behavior verification in tests

**Version Details:**
- **Released:** November 2023
- **Status:** ✅ Active (recent)
- **Maintainer:** Mockito Community
- **JDK Compatibility:** Java 11+

**Usage in Codebase:**
- **IMPORTED BUT NOT USED**
- UserServiceTest imports Mockito but uses real LegacyJdoManager instance
- No mocking actually performed

**Risk Assessment:** 🟢 **LOW**
- Modern version, actively maintained
- Currently unused in tests

**Recommendation:**
- Either use for proper unit testing (mock LegacyJdoManager)
- Or remove to reduce dependencies

---

### External Dependency Summary Table

| Dependency | Version | Status | Usage | Risk | Action |
|------------|---------|--------|-------|------|--------|
| javax.jdo:jdo-api | 3.1 | 🔴 Deprecated | Conventions only | 🔴 CRITICAL | Migrate to JPA |
| guava | 33.0.0-jre | ✅ Active | ❌ Unused | 🟢 LOW | Consider removal |
| junit-jupiter | 5.10.2 | ✅ Active | ✅ Used (1 test) | 🟢 LOW | Expand test coverage |
| mockito-core | 5.8.0 | ✅ Active | ❌ Unused | 🟢 LOW | Use or remove |

---

## Internal Component Dependencies

### Component Dependency Matrix

|  | LegacyJdoManager | LegacyQueries | JdoPropertyKeys | LegacyDbConfig | UserRecord | UserDao | UserService | BillingService |
|---|---|---|---|---|---|---|---|---|
| **LegacyJdoManager** | - | | | | | | | |
| **LegacyQueries** | | - | | | | | | |
| **JdoPropertyKeys** | | | - | | | | | |
| **LegacyDbConfig** | | | ✓ | - | | | | |
| **UserRecord** | | | | | - | | | |
| **UserDao** | ✓ | ✓ | | | | - | | |
| **UserService** | ✓ | | | | | ✓ | - | |
| **BillingService** | ✓ | ✓ | | | | | | - |

**Legend:**
- ✓ = Direct dependency
- - = Self

---

### Detailed Internal Dependencies

#### 1. UserService Dependencies

**Direct Dependencies:**
- `LegacyJdoManager` - Transaction management
- `UserDao` - Data access operations

**Transitive Dependencies:**
- (via UserDao) `LegacyQueries` - SQL definitions

**Dependency Justification:**
- Needs transactions → depends on LegacyJdoManager
- Needs user data access → depends on UserDao

**Coupling Level:** 🟡 Medium (2 direct dependencies)

---

#### 2. UserDao Dependencies

**Direct Dependencies:**
- `LegacyJdoManager` - Query and update execution
- `LegacyQueries` - SQL query definitions

**Transitive Dependencies:** None

**Dependency Justification:**
- Needs to execute queries → depends on LegacyJdoManager
- Needs SQL strings → depends on LegacyQueries

**Coupling Level:** 🟡 Medium (2 direct dependencies)

---

#### 3. BillingService Dependencies

**Direct Dependencies:**
- `LegacyJdoManager` - Transaction and query execution
- `LegacyQueries` - SQL query definitions

**Transitive Dependencies:** None

**Dependency Justification:**
- Needs transactions and query execution → depends on LegacyJdoManager
- Needs SQL strings → depends on LegacyQueries

**Coupling Level:** 🟡 Medium (2 direct dependencies)

**Note:** Bypasses DAO layer (unlike UserService)

---

#### 4. LegacyDbConfig Dependencies

**Direct Dependencies:**
- `JdoPropertyKeys` - Property key constants

**Transitive Dependencies:** None

**Dependency Justification:**
- Needs standard property names → depends on JdoPropertyKeys

**Coupling Level:** 🟢 Low (1 dependency)

---

#### 5. Independent Components (No Dependencies)

**LegacyJdoManager** - Uses only Java standard library  
**LegacyQueries** - Pure static methods with strings  
**JdoPropertyKeys** - Pure constants  
**UserRecord** - Pure data (Java Record)

---

## Transitive Dependencies

### Dependency Chains

#### Chain 1: UserService → UserDao → LegacyJdoManager
```
UserService
    │
    ├─→ LegacyJdoManager (direct)
    │
    └─→ UserDao
         │
         ├─→ LegacyJdoManager (transitive)
         └─→ LegacyQueries (transitive)
```

**Depth:** 2 levels  
**Components:** 4 (UserService, UserDao, LegacyJdoManager, LegacyQueries)

---

#### Chain 2: BillingService → LegacyJdoManager
```
BillingService
    │
    ├─→ LegacyJdoManager (direct)
    └─→ LegacyQueries (direct)
```

**Depth:** 1 level  
**Components:** 3 (BillingService, LegacyJdoManager, LegacyQueries)

---

#### Chain 3: LegacyDbConfig → JdoPropertyKeys
```
LegacyDbConfig
    │
    └─→ JdoPropertyKeys (direct)
```

**Depth:** 1 level  
**Components:** 2 (LegacyDbConfig, JdoPropertyKeys)

---

### Maximum Dependency Depth
**Longest Chain:** UserService → UserDao → LegacyJdoManager  
**Depth:** 3 components  
**Assessment:** 🟢 Shallow (good for testability and maintainability)

---

## Dependency Management

### Build System: Gradle

#### Root Configuration (build.gradle)
```gradle
allprojects {
  group = "com.acme"
  version = "1.0.0"
  repositories { mavenCentral() }
}

subprojects {
  apply plugin: "java"

  java {
    toolchain { languageVersion = JavaLanguageVersion.of(11) }
  }

  dependencies {
    testImplementation "org.junit.jupiter:junit-jupiter:5.10.2"
    testImplementation "org.mockito:mockito-core:5.8.0"
  }

  test { useJUnitPlatform() }
}
```

**Characteristics:**
- Multi-module structure (root + subprojects)
- Java 11 toolchain specified
- Test dependencies applied to all subprojects
- Maven Central as repository

---

#### Module Configuration (legacy-app/build.gradle)
```gradle
dependencies {
  implementation "javax.jdo:jdo-api:3.1"
  implementation "com.google.guava:guava:33.0.0-jre"
}
```

**Characteristics:**
- Only 2 production dependencies
- No version catalogs or BOM
- Direct version specification

---

### Dependency Resolution

**Repository:** Maven Central  
**Resolution Strategy:** Default Gradle (latest matching version)  
**Version Conflicts:** None detected (minimal dependencies)

---

### Dependency Versions

#### Version Management
- ❌ No dependency version management (BOM)
- ❌ No version catalogs
- ❌ No parent POM inheritance
- ✅ Direct version specification (simple but not DRY)

**Recommendation:** Add version management for consistency:
```gradle
// Example with version catalog
dependencyResolutionManagement {
    versionCatalogs {
        libs {
            version('junit', '5.10.2')
            version('mockito', '5.8.0')
            library('junit', 'org.junit.jupiter', 'junit-jupiter').versionRef('junit')
            library('mockito', 'org.mockito', 'mockito-core').versionRef('mockito')
        }
    }
}
```

---

## Dependency Anti-Patterns

### 1. Unused Dependencies
**Issue:** Guava and Mockito declared but not used  
**Impact:** Unnecessary dependency footprint, potential security surface  
**Fix:** Remove or document planned usage

### 2. Deprecated Technology
**Issue:** JDO API from 2013, no active maintenance  
**Impact:** No security patches, no bug fixes, technical debt  
**Fix:** Migrate to JPA 3.x or Spring Data

### 3. No Dependency Management
**Issue:** Direct version specification, no centralized management  
**Impact:** Version drift, inconsistency across modules  
**Fix:** Implement version catalog or BOM

### 4. Package Inconsistency
**Issue:** LegacyDbConfig references wrong package for JdoPropertyKeys  
**Impact:** Confusion, potential compilation issues  
**Fix:** Standardize on one package root

---

## Dependency Health Metrics

### External Dependency Health

| Metric | Score | Assessment |
|--------|-------|------------|
| **Average Age** | ~5.5 years | 🟡 Moderate (skewed by JDO) |
| **Deprecated Count** | 1 / 4 (25%) | 🔴 High |
| **Unused Count** | 2 / 4 (50%) | 🟡 Moderate |
| **Security Vulnerabilities** | 0 known | 🟢 Good |
| **License Compliance** | 100% | ✅ Apache 2.0 compatible |

### Internal Dependency Health

| Metric | Score | Assessment |
|--------|-------|------------|
| **Circular Dependencies** | 0 | ✅ Excellent |
| **Max Dependency Depth** | 3 components | 🟢 Good (shallow) |
| **Highly Coupled Components** | 1 (LegacyJdoManager) | 🟡 Moderate |
| **Independent Components** | 4 / 9 (44%) | 🟢 Good |

---

## Dependency Upgrade Path

### Priority Order

1. **🔴 CRITICAL: Remove JDO Dependency**
   - **Current:** javax.jdo:jdo-api:3.1 (2013)
   - **Target:** Jakarta Persistence (JPA) 3.1
   - **Effort:** 2-3 days
   - **Risk:** High (architectural change)

2. **🟡 MEDIUM: Clean Up Unused Dependencies**
   - **Remove:** com.google.guava:guava:33.0.0-jre (if truly unused)
   - **Action:** Use Mockito or remove it
   - **Effort:** 1 hour
   - **Risk:** Low

3. **🟢 LOW: Update Test Dependencies**
   - **Current:** JUnit 5.10.2, Mockito 5.8.0
   - **Target:** Latest versions (if newer available)
   - **Effort:** 30 minutes
   - **Risk:** Very low

---

## Dependency Isolation

### Blast Radius Analysis

**If javax.jdo:jdo-api removed:**
- 🔴 **BREAKS:** JdoPropertyKeys, LegacyDbConfig
- 🟡 **MAY IMPACT:** All components using properties
- **Components Affected:** 2 directly, 9 transitively

**If guava removed:**
- ✅ **NO IMPACT:** Zero usage in codebase

**If junit-jupiter removed:**
- 🔴 **BREAKS:** UserServiceTest
- **Components Affected:** 1 test class

**If mockito-core removed:**
- ✅ **NO IMPACT:** Imported but not used

---

## Related Documentation

- [Dependency Analysis (Detailed)](../analysis/dependency-analysis.md)
- [Component Architecture](components.md)
- [Technical Debt - Outdated Components](../technical-debt/outdated-components.md)
- [Migration Strategy](../migration/component-order.md)

---

*Dependency documentation based on static analysis of build files and source code.*

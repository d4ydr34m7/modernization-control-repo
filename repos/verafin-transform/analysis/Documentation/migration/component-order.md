# Component Migration Order

**Project:** transform-jdo-demo  
**Purpose:** Define the correct order for migrating components during modernization  
**Strategy:** Bottom-up dependency migration

---

## Migration Strategy Overview

Components must be migrated in **bottom-up dependency order** to ensure:
1. No component depends on unmigrated code
2. Each component can be tested independently
3. Migration can be paused at any phase boundary
4. Rollback is possible at phase boundaries

---

## Dependency Analysis

### Component Dependency Graph

```
                    ┌─────────────┐
                    │   Client    │
                    │ Application │
                    └──────┬──────┘
                           │
                  ┌────────┴────────┐
                  │                 │
           ┌──────▼──────┐   ┌──────▼────────┐
           │ UserService │   │BillingService │
           └──────┬──────┘   └──────┬────────┘
                  │                 │
                  └────────┬────────┘
                           │
                    ┌──────▼──────┐
                    │   UserDao   │
                    └──────┬──────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
        ┌────────▼────────┐   ┌──────▼──────┐
        │LegacyJdoManager │   │ UserRecord  │
        └────────┬────────┘   └─────────────┘
                 │
        ┌────────┴────────┐
        │                 │
  ┌─────▼──────┐  ┌───────▼──────┐
  │LegacyQueries│  │LegacyDbConfig│
  └─────┬──────┘  └───────┬──────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │JdoPropertyKeys  │
        └─────────────────┘
```

---

## Phase 1: Foundation Components (No Dependencies)

**Duration:** 1-2 days  
**Risk:** 🟢 LOW

### Components

#### 1.1 JdoPropertyKeys
- **Current:** `com.acme.legacy.jdo.JdoPropertyKeys`
- **File:** `legacy-app/src/main/java/com/acme/legacy/jdo/JdoPropertyKeys.java`
- **Lines of Code:** 8
- **Dependencies:** None
- **Dependents:** LegacyDbConfig

**Migration Action:**
- Fix package name to `com.transformtest.legacy.jdo`
- No functional changes needed

#### 1.2 LegacyQueries
- **Current:** `com.transformtest.legacy.jdo.LegacyQueries`
- **File:** `legacy-app/src/main/java/com/transformtest/legacy/jdo/LegacyQueries.java`
- **Lines of Code:** 8
- **Dependencies:** None
- **Dependents:** LegacyJdoManager, UserDao, BillingService

**Migration Action:**
- Convert to JPQL queries or keep as SQL constants
- Add query validation
- Document parameter requirements

**Validation:**
- ✅ Both classes compile independently
- ✅ No test failures
- ✅ Package names consistent

---

## Phase 2: Configuration & Manager Layer

**Duration:** 2-3 days  
**Risk:** 🟡 MEDIUM  
**Depends on:** Phase 1

### Components

#### 2.1 LegacyDbConfig → SecureDbConfig
- **Current:** `com.acme.legacy.config.LegacyDbConfig`
- **File:** `legacy-app/src/main/java/com/acme/legacy/config/LegacyDbConfig.java`
- **Lines of Code:** 12
- **Dependencies:** JdoPropertyKeys (Phase 1)
- **Dependents:** LegacyJdoManager

**Migration Actions:**
1. Fix package name to `com.transformtest.legacy.config`
2. Replace with SecureDbConfig using AWS Secrets Manager
3. Remove hardcoded credentials
4. Add caching for secret values

**Target Implementation:**
```java
package com.transformtest.legacy.config;

public final class SecureDbConfig {
  private static JsonNode cachedSecret = null;
  
  private static synchronized JsonNode getSecret() {
    if (cachedSecret == null) {
      try (SecretsManagerClient client = SecretsManagerClient.create()) {
        GetSecretValueRequest request = GetSecretValueRequest.builder()
          .secretId("prod/database/legacy-app")
          .build();
        
        GetSecretValueResponse response = client.getSecretValue(request);
        cachedSecret = mapper.readTree(response.secretString());
      } catch (Exception e) {
        throw new RuntimeException("Cannot load database configuration", e);
      }
    }
    return cachedSecret;
  }
  
  public static String user() {
    return getSecret().get("username").asText();
  }
  
  public static String password() {
    return getSecret().get("password").asText();
  }
  
  public static String url() {
    return getSecret().get("url").asText();
  }
}
```

**Validation:**
- ✅ Credentials loaded from Secrets Manager
- ✅ No hardcoded values remain
- ✅ Local development uses environment variable fallback

#### 2.2 LegacyJdoManager → JpaEntityManager
- **Current:** `com.transformtest.legacy.jdo.LegacyJdoManager`
- **File:** `legacy-app/src/main/java/com/transformtest/legacy/jdo/LegacyJdoManager.java`
- **Lines of Code:** 34
- **Dependencies:** LegacyDbConfig (Phase 2.1)
- **Dependents:** UserDao, UserService, BillingService

**Migration Actions:**
1. Remove stateful `ConcurrentHashMap`
2. Replace with JPA `EntityManager`
3. Convert `executeQuery()` to typed queries
4. Convert `executeUpdate()` to typed updates
5. Remove manual transaction management (use `@Transactional`)

**Target Implementation:**
```java
@Repository
public class EntityManagerWrapper {
  
  @PersistenceContext
  private EntityManager entityManager;
  
  public <T> List<T> executeQuery(String jpql, Map<String, Object> params, Class<T> resultClass) {
    TypedQuery<T> query = entityManager.createQuery(jpql, resultClass);
    params.forEach(query::setParameter);
    return query.getResultList();
  }
  
  public int executeUpdate(String jpql, Map<String, Object> params) {
    Query query = entityManager.createQuery(jpql);
    params.forEach(query::setParameter);
    return query.executeUpdate();
  }
  
  // begin(), commit(), rollback() handled by @Transactional
}
```

**Validation:**
- ✅ Stateless design (no internal state)
- ✅ Thread-safe
- ✅ Transaction management via Spring
- ✅ All tests passing

---

## Phase 3: Data Models

**Duration:** 1 day  
**Risk:** 🟢 LOW  
**Depends on:** None (independent)

### Components

#### 3.1 UserRecord → User Entity
- **Current:** `com.transformtest.legacy.user.UserRecord`
- **File:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserRecord.java`
- **Lines of Code:** 25
- **Dependencies:** None
- **Dependents:** UserDao, UserService

**Migration Actions:**
1. Convert to JPA `@Entity`
2. Add proper field annotations
3. Implement equals/hashCode properly
4. Add validation annotations

**Target Implementation:**
```java
@Entity
@Table(name = "users")
public class User {
  
  @Id
  @Column(length = 50)
  private String id;
  
  @Column(nullable = false, unique = true, length = 255)
  @Email
  private String email;
  
  @Column(length = 20)
  private String status;
  
  // Constructors, getters, setters
  
  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof User)) return false;
    User user = (User) o;
    return Objects.equals(id, user.id);
  }
  
  @Override
  public int hashCode() {
    return Objects.hash(id);
  }
}
```

**Validation:**
- ✅ Entity properly mapped to database table
- ✅ All fields have correct types and constraints
- ✅ equals/hashCode based on ID only

---

## Phase 4: Data Access Layer

**Duration:** 2-3 days  
**Risk:** 🟡 MEDIUM  
**Depends on:** Phases 2, 3

### Components

#### 4.1 UserDao → UserRepository
- **Current:** `com.transformtest.legacy.user.UserDao`
- **File:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserDao.java`
- **Lines of Code:** 30
- **Dependencies:** LegacyJdoManager (Phase 2), LegacyQueries (Phase 1), UserRecord (Phase 3)
- **Dependents:** UserService

**Migration Actions:**
1. Replace with Spring Data JPA repository
2. Convert queries to JPQL or method name queries
3. Remove manual result mapping
4. Add query validation

**Target Implementation:**
```java
@Repository
public interface UserRepository extends JpaRepository<User, String> {
  
  @Query("SELECT u FROM User u WHERE u.id = :id")
  Optional<User> findById(@Param("id") String id);
  
  @Modifying
  @Query("UPDATE User u SET u.email = :email WHERE u.id = :id")
  int updateEmail(@Param("id") String id, @Param("email") String email);
  
  Optional<User> findByEmail(String email);
}
```

**Validation:**
- ✅ All DAO methods converted to repository methods
- ✅ Queries return correct types (no Map<String, Object>)
- ✅ Integration tests pass

---

## Phase 5: Service Layer

**Duration:** 3-5 days  
**Risk:** 🔴 HIGH (Business Logic)  
**Depends on:** Phase 4

### Components

#### 5.1 UserService
- **Current:** `com.transformtest.legacy.user.UserService`
- **File:** `legacy-app/src/main/java/com/transformtest/legacy/user/UserService.java`
- **Lines of Code:** 27
- **Dependencies:** UserDao (Phase 4), LegacyJdoManager (Phase 2)
- **Dependents:** Client code

**Migration Actions:**
1. Inject `UserRepository` instead of `UserDao`
2. Remove manual transaction management
3. Add `@Transactional` annotation
4. Add logging
5. Implement proper exception handling
6. Add input validation

**Target Implementation:**
```java
@Service
@Transactional
public class UserService {
  private static final Logger log = LoggerFactory.getLogger(UserService.class);
  
  private final UserRepository userRepository;
  
  @Autowired
  public UserService(UserRepository userRepository) {
    this.userRepository = userRepository;
  }
  
  public boolean changeEmail(@Valid ChangeEmailRequest request) 
      throws UserNotFoundException, EmailUpdateException {
    
    log.info("Changing email: userId={}", request.getUserId());
    
    User user = userRepository.findById(request.getUserId())
      .orElseThrow(() -> new UserNotFoundException(request.getUserId()));
    
    user.setEmail(request.getNewEmail());
    userRepository.save(user);
    
    log.info("Email changed successfully: userId={}", request.getUserId());
    return true;
  }
}
```

**Validation:**
- ✅ No manual transaction management
- ✅ Proper exception handling
- ✅ Logging in place
- ✅ Input validation working
- ✅ All tests passing
- ✅ Integration tests pass

#### 5.2 BillingService
- **Current:** `com.transformtest.legacy.billing.BillingService`
- **File:** `legacy-app/src/main/java/com/transformtest/legacy/billing/BillingService.java`
- **Lines of Code:** 31
- **Dependencies:** LegacyJdoManager (Phase 2), LegacyQueries (Phase 1)
- **Dependents:** Client code

**Migration Actions:**
1. Create Invoice entity
2. Create InvoiceRepository
3. Replace JDO manager with repository
4. Add `@Transactional`
5. Add logging and validation

**Target Implementation:**
```java
@Service
@Transactional
public class BillingService {
  private static final Logger log = LoggerFactory.getLogger(BillingService.class);
  
  private final InvoiceRepository invoiceRepository;
  
  @Autowired
  public BillingService(InvoiceRepository invoiceRepository) {
    this.invoiceRepository = invoiceRepository;
  }
  
  public long createInvoice(@Valid CreateInvoiceRequest request) 
      throws InvoiceCreationException {
    
    log.info("Creating invoice: userId={}, amount={}", 
             request.getUserId(), request.getAmount());
    
    Invoice invoice = new Invoice();
    invoice.setUserId(request.getUserId());
    invoice.setAmount(request.getAmount());
    
    Invoice saved = invoiceRepository.save(invoice);
    
    log.info("Invoice created: invoiceId={}, userId={}, amount={}", 
             saved.getId(), request.getUserId(), request.getAmount());
    
    return saved.getId();
  }
}
```

**Validation:**
- ✅ Invoice entity created
- ✅ Repository implemented
- ✅ Transaction management automatic
- ✅ Logging and validation in place
- ✅ All tests passing

---

## Phase 6: Test Suite

**Duration:** 1-2 days  
**Risk:** 🟢 LOW  
**Depends on:** All previous phases

### Components

#### 6.1 UserServiceTest
- **Current:** `com.transformtest.legacy.user.UserServiceTest`
- **File:** `legacy-app/src/test/java/com/transformtest/legacy/user/UserServiceTest.java`
- **Lines of Code:** 14
- **Dependencies:** UserService (Phase 5)

**Migration Actions:**
1. Update mocks to use new repository interfaces
2. Add tests for new exception types
3. Add validation tests
4. Add logging verification

**Validation:**
- ✅ All tests updated and passing
- ✅ 80%+ code coverage achieved
- ✅ Integration tests pass

---

## Migration Timeline

```
Week 1:
├── Day 1-2: Phase 1 (Foundation)
├── Day 3-5: Phase 2 (Config & Manager)

Week 2:
├── Day 1: Phase 3 (Data Models)
├── Day 2-4: Phase 4 (Data Access)
├── Day 5: Phase 5 Start (User Service)

Week 3:
├── Day 1-2: Phase 5 Continue (Billing Service)
├── Day 3-4: Phase 6 (Test Suite)
├── Day 5: Integration Testing & Cleanup

Week 4:
├── Day 1-2: Performance Testing
├── Day 3-4: Documentation
├── Day 5: Final Validation & Release
```

**Total Duration:** 4 weeks  
**Team Size:** 1-2 engineers  
**Risk Level:** 🟡 MEDIUM

---

## Rollback Strategy

### Phase Boundaries as Rollback Points

Each phase boundary is a safe rollback point:

**Phase 1 → Phase 2:**
- Roll back: Revert package name changes
- Impact: Minimal (config only)

**Phase 2 → Phase 3:**
- Roll back: Revert SecureDbConfig and JPA manager
- Impact: Low (infrastructure only)

**Phase 3 → Phase 4:**
- Roll back: Remove entity annotations, restore UserRecord
- Impact: Low (data model only)

**Phase 4 → Phase 5:**
- Roll back: Restore DAO implementation
- Impact: Medium (data access layer)

**Phase 5 → Production:**
- Roll back: Restore old service implementations
- Impact: High (business logic)

### Feature Flags

Use feature flags for gradual rollout:

```java
@Service
public class UserService {
  
  @Value("${feature.jpa.enabled:false}")
  private boolean jpaEnabled;
  
  public boolean changeEmail(String userId, String newEmail) {
    if (jpaEnabled) {
      return changeEmailJpa(userId, newEmail);  // New implementation
    } else {
      return changeEmailLegacy(userId, newEmail);  // Old implementation
    }
  }
}
```

---

## Success Criteria

### Phase Completion Criteria

Each phase must meet these criteria before proceeding:

1. **Code Quality**
   - ✅ All code compiles
   - ✅ No compiler warnings
   - ✅ Code review approved

2. **Testing**
   - ✅ Unit tests pass
   - ✅ Integration tests pass
   - ✅ Coverage maintained or improved

3. **Documentation**
   - ✅ Migration notes updated
   - ✅ API changes documented
   - ✅ Rollback procedure documented

4. **Performance**
   - ✅ Performance equivalent or better
   - ✅ No memory leaks
   - ✅ No increased error rates

---

## Related Documentation

- [Test Specifications](test-specifications.md) - Testing requirements for each phase
- [Validation Criteria](validation-criteria.md) - Acceptance criteria
- [Technical Debt Remediation Plan](../technical-debt/remediation-plan.md) - Overall plan

---

*Last Updated: 2026-01-18*  
*Owner: Engineering Lead*  
*Next Review: Start of each phase*

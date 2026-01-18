# JDO to JPA Migration Guide

**Project:** transform-jdo-demo  
**Migration Path:** JDO 3.1 → JPA 3.1 with Hibernate

---

## Migration Strategy

### Phase 1: Add JPA Dependencies

```gradle
dependencies {
  //  implementation "javax.jdo:jdo-api:3.1"  // Remove
  implementation "jakarta.persistence:jakarta.persistence-api:3.1.0"
  implementation "org.hibernate:hibernate-core:6.4.1"
  implementation "org.postgresql:postgresql:42.7.1"
}
```

### Phase 2: Convert Entities

**Before (JDO):**
```java
public class UserRecord {
  private String id;
  private String email;
  private String status;
}
```

**After (JPA):**
```java
@Entity
@Table(name = "users")
public class User {
  @Id
  private String id;
  
  @Column(nullable = false)
  private String email;
  
  private String status;
}
```

### Phase 3: Replace Manager with EntityManager

**Before:**
```java
public class LegacyJdoManager {
  public List<Map<String, Object>> executeQuery(String sql, Map<String, Object> params) { ... }
}
```

**After:**
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
}
```

### Phase 4: Use Spring Data JPA (Recommended)

```java
@Repository
public interface UserRepository extends JpaRepository<User, String> {
  Optional<User> findById(String id);
  
  @Modifying
  @Query("UPDATE User u SET u.email = :email WHERE u.id = :id")
  int updateEmail(@Param("id") String id, @Param("email") String email);
}
```

---

## Complete Migration Steps

1. Add JPA dependencies
2. Create JPA entities with @Entity annotations
3. Create Spring Data repositories
4. Update service classes to use repositories
5. Replace manual transaction management with @Transactional
6. Remove JDO dependencies
7. Test thoroughly
8. Deploy

**Estimated Effort:** 2-3 weeks

---

*Last Updated: 2026-01-18*

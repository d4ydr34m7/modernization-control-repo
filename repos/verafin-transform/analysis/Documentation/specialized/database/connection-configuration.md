# Database Connection Configuration

**Project:** transform-jdo-demo  
**Database:** PostgreSQL  
**Connection Method:** JDBC via JDO properties

---

## Configuration Properties

### JDO Property Keys

**File:** `com.acme.legacy.jdo.JdoPropertyKeys`

```java
public final class JdoPropertyKeys {
  public static final String CONNECTION_URL = "javax.jdo.option.ConnectionURL";
  public static final String CONNECTION_USER = "javax.jdo.option.ConnectionUserName";
  public static final String CONNECTION_PWD = "javax.jdo.option.ConnectionPassword";
}
```

---

## Current Configuration (🔴 INSECURE)

**File:** `com.acme.legacy.config.LegacyDbConfig`

```java
public static String user() {
  return System.getProperty(JdoPropertyKeys.CONNECTION_USER, "legacy_user");
  // 🔴 Hardcoded default username
}

public static String password() {
  return System.getProperty(JdoPropertyKeys.CONNECTION_PWD, "legacy_pwd");
  // 🔴 Hardcoded default password
}

public static String url() {
  return System.getProperty(JdoPropertyKeys.CONNECTION_URL, 
    "jdbc:postgresql://localhost:5432/legacy");
  // 🔴 Hardcoded default URL
}
```

**Issues:**
- Plaintext passwords
- Hardcoded defaults
- Credentials in system properties

---

## Connection String Format

**Pattern:**
```
jdbc:postgresql://<host>:<port>/<database>?<options>
```

**Default:**
```
jdbc:postgresql://localhost:5432/legacy
```

**Production Example:**
```
jdbc:postgresql://prod-db.example.com:5432/legacydb?ssl=true&sslmode=require
```

---

## Recommended Configuration (✅ SECURE)

### Option 1: AWS Secrets Manager

```java
public static String password() {
  SecretsManagerClient client = SecretsManagerClient.create();
  GetSecretValueResponse response = client.getSecretValue(
    GetSecretValueRequest.builder()
      .secretId("prod/database/legacy-app")
      .build()
  );
  JsonNode secret = objectMapper.readTree(response.secretString());
  return secret.get("password").asText();
}
```

### Option 2: Environment Variables

```java
public static String password() {
  String pwd = System.getenv("DB_PASSWORD");
  if (pwd == null || pwd.isEmpty()) {
    throw new IllegalStateException("DB_PASSWORD not configured");
  }
  return pwd;
}
```

---

## Connection Pool Configuration

**Recommended Settings:**
```properties
# Minimum connections
hibernate.c3p0.min_size=5

# Maximum connections
hibernate.c3p0.max_size=20

# Timeout
hibernate.c3p0.timeout=300

# Max statements
hibernate.c3p0.max_statements=50
```

---

*Last Updated: 2026-01-18*

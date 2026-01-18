# Gradle Build Configuration

**Project:** transform-jdo-demo  
**Build System:** Gradle 8.x  
**Java Version:** 11 (LTS)

---

## Project Structure

```
transform-jdo-demo/
├── build.gradle (root)
├── settings.gradle
├── gradle.properties
└── legacy-app/
    ├── build.gradle (module)
    └── src/
        ├── main/java/
        └── test/java/
```

---

## Root build.gradle

```gradle
plugins {
  id 'java'
}

allprojects {
  group = 'com.transformtest'
  version = '1.0.0'
}

subprojects {
  apply plugin: 'java'
  
  java {
    toolchain {
      languageVersion = JavaLanguageVersion.of(11)
    }
  }
  
  repositories {
    mavenCentral()
  }
  
  dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'
    testImplementation 'org.mockito:mockito-core:5.8.0'
  }
  
  test {
    useJUnitPlatform()
  }
}
```

---

## legacy-app/build.gradle

```gradle
dependencies {
  // Legacy persistence (🔴 DEPRECATED)
  implementation "javax.jdo:jdo-api:3.1"
  
  // Utilities
  implementation "com.google.guava:guava:33.0.0-jre"  // ⚠️ Unused
  
  // Test dependencies (inherited from root)
}
```

**Issues:**
- JDO API is deprecated (11+ years old)
- Guava declared but not used
- No logging framework

---

## settings.gradle

```gradle
rootProject.name = 'transform-jdo-demo'
include 'legacy-app'
```

---

## gradle.properties

```properties
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
org.gradle.caching=true
```

---

## Recommended Improvements

### 1. Add Logging

```gradle
dependencies {
  implementation "org.slf4j:slf4j-api:2.0.9"
  implementation "ch.qos.logback:logback-classic:1.4.14"
}
```

### 2. Add Code Coverage

```gradle
plugins {
  id 'jacoco'
}

jacoco {
  toolVersion = "0.8.11"
}

jacocoTestReport {
  reports {
    xml.required = true
    html.required = true
  }
}

test {
  finalizedBy jacocoTestReport
}
```

### 3. Migrate to JPA

```gradle
dependencies {
  // Remove:
  // implementation "javax.jdo:jdo-api:3.1"
  
  // Add:
  implementation "jakarta.persistence:jakarta.persistence-api:3.1.0"
  implementation "org.hibernate:hibernate-core:6.4.1"
  implementation "org.postgresql:postgresql:42.7.1"
}
```

### 4. Remove Unused Dependencies

```gradle
dependencies {
  // Remove (unused):
  // implementation "com.google.guava:guava:33.0.0-jre"
}
```

---

## Build Commands

```bash
# Clean build
./gradlew clean build

# Run tests
./gradlew test

# Generate coverage report
./gradlew test jacocoTestReport

# Run specific test
./gradlew test --tests UserServiceTest

# Build without tests
./gradlew build -x test
```

---

*Last Updated: 2026-01-18*

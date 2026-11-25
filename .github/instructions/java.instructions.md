---
name: "Java Coding Standards"
description: "Use when writing or modifying Java, Spring Boot, JPA, or JUnit code in backend-java. Covers Java 21 style, layering, validation, API contracts, persistence, and tests."
applyTo: "backend-java/**/*.java"
---
# Java Coding Standards

- Target Java 21 and follow the existing Spring Boot 3 project style.
- Use four spaces for indentation, one top-level type per file, and conventional names: `UpperCamelCase` for types, `lowerCamelCase` for methods and fields, and `UPPER_SNAKE_CASE` for constants.
- Prefer immutable data where practical. Use records for request and response DTOs when they are data carriers, and use `final` fields with constructor injection for Spring dependencies.
- Keep package responsibilities separate: controllers translate HTTP requests and responses, services own validation and business rules, and repositories own all database access. Do not put SQL or business rules in controllers.
- Use Jakarta Bean Validation on inbound request DTOs and preserve the API contract: missing titles and unknown statuses return HTTP 422, while missing IDs return HTTP 404.
- Keep the database schema authoritative. Do not add JPA schema-generation settings, migrations, or application-side timestamp assignments when working on the model layer.
- Prefer `Optional` for repository lookups, throw the project’s domain exceptions for missing or invalid values, and avoid returning `null` from service methods unless the existing API explicitly requires it.
- Prefer standard Java and Spring APIs such as streams, `List.toList()`, `StringUtils.hasText`, and `ResponseEntity` when they match nearby code. Avoid speculative abstractions and broad refactors.
- Keep public endpoint request and response shapes aligned with the other backends and existing contracts.
- Add or update focused tests for every behavior or endpoint change. Use JUnit 5, Mockito, and AssertJ in the established style, and test both successful behavior and relevant validation or exception paths.
- Run `./mvnw -B test` from `backend-java/` after Java changes.

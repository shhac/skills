# Verification commands by toolchain

The lead consults this when running the [verification loop](conventions.md#verification-loop). Detect the toolchain from the repo's marker files, then run every applicable check (tests + typecheck + lint).

This catalog is not exhaustive. The "When nothing matches" section at the bottom is the canonical fallback — use it whenever the project doesn't fit, or fits only partially.

## JavaScript / TypeScript / Node

Marker: `package.json`

| Check     | Command (typical)                              | Notes                                                              |
|-----------|------------------------------------------------|--------------------------------------------------------------------|
| Tests     | `npm test`                                     | Inspect `scripts.test` in `package.json`. Use `pnpm`/`yarn`/`bun` if a corresponding lockfile is present. |
| Typecheck | `npm run typecheck` or `npx tsc --noEmit`      | Only if a `typecheck` script exists or `tsconfig.json` is present. |
| Lint      | `npm run lint`                                 | Only if a `lint` script exists.                                    |

## Python

Marker: `pyproject.toml`, `setup.py`, `setup.cfg`, `pytest.ini`, `tox.ini`

| Check     | Command (typical)                              |
|-----------|------------------------------------------------|
| Tests     | `pytest`                                       |
| Typecheck | `mypy .` or `pyright`                          |
| Lint      | `ruff check .` or `flake8`                     |

## Rust

Marker: `Cargo.toml`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `cargo test`                                   |
| Typecheck | `cargo check`                                  |
| Lint      | `cargo clippy -- -D warnings`                  |

## Go

Marker: `go.mod`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `go test ./...`                                |
| Typecheck | `go build ./...`                               |
| Lint      | `go vet ./...` and/or `golangci-lint run`      |

## OCaml

Marker: `dune-project`, `*.opam`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `dune test` (alias for `dune runtest`)         |
| Typecheck | `dune build`                                   |
| Lint      | (no standard; check project conventions)       |

## .NET (C#, F#, VB)

Marker: `*.sln`, `*.csproj`, `*.fsproj`, `*.vbproj`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `dotnet test`                                  |
| Typecheck | `dotnet build`                                 |
| Lint      | `dotnet format --verify-no-changes`            |

## Elixir / Erlang

Marker: `mix.exs` (Elixir), `rebar.config` (Erlang)

| Check     | Elixir                | Erlang                            |
|-----------|-----------------------|-----------------------------------|
| Tests     | `mix test`            | `rebar3 eunit` and/or `rebar3 ct` |
| Typecheck | `mix dialyzer`        | `rebar3 dialyzer`                 |
| Lint      | `mix credo`           | (project-specific)                |

## Haskell

Marker: `*.cabal`, `stack.yaml`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `cabal test` or `stack test`                   |
| Typecheck | `cabal build` or `stack build`                 |
| Lint      | `hlint .`                                      |

## Java / Kotlin / Scala

Marker: `pom.xml` (Maven), `build.gradle{,.kts}` (Gradle), `build.sbt` (sbt)

| Check     | Maven                  | Gradle                   | sbt           |
|-----------|------------------------|--------------------------|---------------|
| Tests     | `mvn test`             | `./gradlew test`         | `sbt test`    |
| Typecheck | `mvn compile`          | `./gradlew compileJava`  | `sbt compile` |
| Lint      | `mvn checkstyle:check` | `./gradlew check`        | (project-specific) |

## Ruby

Marker: `Gemfile`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `bundle exec rspec` or `bundle exec rake test` |
| Lint      | `bundle exec rubocop`                          |

## Swift

Marker: `Package.swift`, `*.xcodeproj`, `*.xcworkspace`

| Check     | Command                                        |
|-----------|------------------------------------------------|
| Tests     | `swift test` (SPM) or `xcodebuild test ...`    |
| Typecheck | `swift build` or `xcodebuild build ...`        |
| Lint      | `swiftlint`                                    |

## Make / Just / Bazel / custom

Markers: `Makefile`, `justfile`, `BUILD`/`BUILD.bazel`/`WORKSPACE`, project-specific scripts.

If `Makefile` defines `test`, `check`, or `lint` targets, prefer those — projects with Makefiles usually mean for them to be canonical entry points. Same for `justfile` recipes. For Bazel, `bazel test //...` is the standard.

## When nothing matches

This is the canonical fallback — reach for it whenever the project doesn't appear above, has a non-standard layout, or has the marker file but the standard command fails:

1. Read the project's `README.md`, `CONTRIBUTING.md`, and CI config (`.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/config.yml`, etc.) to find the actual verify commands.
2. If still ambiguous, ask the user how to verify.
3. Do not proceed with autonomous changes that require verification when no verification path is established — surface this to the user and pause. Per the [verification loop](conventions.md#verification-loop), "no tooling detected" is not equivalent to "passed".

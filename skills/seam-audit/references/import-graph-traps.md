# Import-Graph Traps

Static `import` / `require` / `use` analysis catches most module-to-module edges, but a meaningful fraction of real dependencies don't show up in the file's imports. This file lists the patterns that silently undercount seams, and how to mark them in the report.

## Why this matters

A seam audit that misses these will produce a *false* topology: modules look narrower than they are, accidental hubs look fine. The skill's correctness depends on either (a) accounting for them, or (b) calling out the blind spot via the `uncertain-import-graph` flag and a `Limitations` line.

## The traps

### 1. Dynamic / lazy imports

`import("./foo")` (JS), `__import__()` (Python), `Class.forName()` (Java), `require_relative` in a loop (Ruby), etc.

- **What you'll miss:** an edge from the dynamic-import site to the loaded module.
- **How to detect:** grep for `import\(`, `dynamic[_-]?import`, language-specific equivalents.
- **What to do:** add the edge if the target is determinable from the surrounding code; flag `uncertain-import-graph` if it's a variable / config-driven path.

### 2. Dependency injection containers

Classes registered with a container at startup; consumers receive instances via constructor injection, not direct imports. NestJS modules, InversifyJS, Spring `@Autowired`, ASP.NET DI, Symfony, FastAPI dependencies.

- **What you'll miss:** the consumer's actual dependency on the registered class. The consumer imports the *interface* or a token, not the implementation.
- **How to detect:** look for DI configuration files (`module.ts`, `*.module.ts`, `application-context.xml`, etc.) and trace registrations.
- **What to do:** treat the registered class as having seams from its consumers via the DI config. If you can't trace it cleanly, flag the consumers AND the registration module with `uncertain-import-graph`.

### 3. Framework routing / autoload

Routes registered by filesystem convention (Next.js app router, Astro pages, Rails autoload, Laravel routes, Django URL patterns), Spring Boot component-scan, Phoenix routers.

- **What you'll miss:** the framework imports your handler module, but there's no static `import` line proving it. The handler looks like it has zero incoming seams.
- **How to detect:** identify the convention. Next.js/Astro: any file under `pages/` or `app/` is auto-routed. Rails: `app/` directories autoload. Spring: `@Component` classes.
- **What to do:** treat the framework's auto-discovery as an incoming seam from a synthetic `framework:routes` source. Mark the handler `external-heavy` if appropriate.

### 4. Barrel files / re-export modules

`index.ts` files that re-export from siblings. Common in JS/TS, less in other languages.

- **What you'll miss:** the barrel will look like an enormous hub (huge fan-out + huge fan-in), but it's an intentional API surface.
- **How to detect:** file consists almost entirely of `export { ... } from "./..."` / `export * from "./..."`.
- **What to do:** classify as `hub-by-design` with role *"public API barrel"*. Don't flag. Optionally count "transitive seams" — what the consumers of the barrel ultimately reach — if a sibling-import-vs-barrel-import distinction would matter to the reader.

### 5. Plugin / extension systems

Webpack loaders, Babel plugins, Vite plugins, ESLint rules, Vim plugins. Loaded by configuration, not imports.

- **What you'll miss:** the plugin host's dependency on the plugin.
- **How to detect:** scan `*.config.{js,ts}`, `package.json` plugin arrays, lockfiles.
- **What to do:** add a synthetic seam from the config to each plugin. The plugin itself is `external-heavy` if it lives in node_modules.

### 6. Template / asset references

A `<Foo />` in a template that doesn't `import Foo` (some frameworks register components globally — Vue with global registration, Angular modules with `declarations`).

- **What you'll miss:** the template's seam to the component.
- **How to detect:** language-specific. Vue 2 `Vue.component(...)`, Angular `@NgModule({ declarations })`.
- **What to do:** trace the global registration site. Add the seam manually.

### 7. String-based references

Module names stored as strings and resolved at runtime: `getModule("foo/bar")`, message-bus topic names that map to handler files, GraphQL resolver-name conventions, CQRS command bus.

- **What you'll miss:** the entire string-resolved edge.
- **How to detect:** look for resolver registries, message buses, service locators.
- **What to do:** add the edge if the registry is exhaustive and traceable. Otherwise mark the resolver module with `uncertain-import-graph` and note the trace gap.

### 8. Type-only imports vs. runtime imports

TypeScript `import type` declarations. Build systems strip them; they don't appear in the compiled output. Some linters and grep patterns count them, others don't.

- **What you'll miss:** depends on the tooling. A grep for `^import` will catch them; a runtime-graph tool may not.
- **What to do:** count `import type` as an outgoing seam (the type-level dependency is real for code-comprehension and refactor purposes), but note the policy in the threshold-disclosure line if it differs from the obvious.

### 9. Side-effect-only imports

`import "./bootstrap";` — no symbol imported, but the file runs and may register handlers, monkey-patch globals, etc.

- **What you'll miss:** nothing if your grep picks up bare imports — these *do* show as static imports.
- **What to do:** count as one outgoing seam. The bootstrap file likely has high incoming seam count *to no purpose visible from the imports* — describe its role explicitly in the table (`role: "side-effect bootstrap"`).

## Decision rubric

For each module, after gathering static imports, ask:

1. Does the codebase use any of the trap patterns above?
2. If yes, can I trace the trap edges cleanly (config files exhaustive, registry deterministic)?
   - **Yes:** add the edges. The module's seams are now correct.
   - **No:** flag `uncertain-import-graph` and add a `Limitations` line to the report's preamble.
3. If the trap is global (e.g. the whole repo uses DI), state it once in the `Limitations` line and don't flag every consumer — that drowns the signal.

## What this skill explicitly does NOT do

- Type-level coupling beyond `import type` (e.g. structural-type assignability that creates de-facto dependencies without imports).
- Compile-time macro expansion / code generation (e.g. Rust `proc_macro`, C preprocessor) — these synthesize dependencies that vanish from the source.
- Build-time configuration (Vite aliases, TypeScript paths) that reroutes imports — record the apparent target, not the resolved one.

These are out of scope. Note the gap if relevant; don't try to model it.


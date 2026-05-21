import subprocess
import os

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def _ok(text):
    return type("R", (), {"stdout": str(text)})()

ACTIONS = {
    "rust_run":           {"description": "Run a Rust file with rustc, args = [file.rs]",                    "execute": lambda a: _run(f'rustc "{a[0]}" -o "{a[0][:-3]}" && "{a[0][:-3]}"')},
    "rust_cargo_run":     {"description": "cargo run in a folder, args = [folder_path]",                     "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo run')},
    "rust_cargo_build":   {"description": "cargo build, args = [folder_path]",                               "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo build')},
    "rust_cargo_release": {"description": "cargo build --release, args = [folder_path]",                     "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo build --release')},
    "rust_cargo_test":    {"description": "cargo test, args = [folder_path]",                                "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo test')},
    "rust_cargo_new":     {"description": "Create new Rust project, args = [project_name]",                  "execute": lambda a: _run(f"cargo new {a[0]}")},
    "rust_cargo_add":     {"description": "Add a dependency, args = [folder_path, crate_name]",              "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo add {a[1]}')},
    "rust_cargo_clean":   {"description": "cargo clean, args = [folder_path]",                               "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo clean')},
    "rust_cargo_fmt":     {"description": "Format Rust code, args = [folder_path]",                          "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo fmt')},
    "rust_cargo_clippy":  {"description": "Run clippy linter, args = [folder_path]",                         "execute": lambda a: _run(f'cd /d "{a[0]}" && cargo clippy')},
    "rust_version":       {"description": "Get Rust/cargo version",                                           "execute": lambda a: _run("rustc --version && cargo --version")},

    "go_run":             {"description": "Run a Go file, args = [file.go]",                                  "execute": lambda a: _run(f'go run "{a[0]}"')},
    "go_build":           {"description": "Build a Go project, args = [folder_path]",                        "execute": lambda a: _run(f'cd /d "{a[0]}" && go build ./...')},
    "go_test":            {"description": "Run Go tests, args = [folder_path]",                               "execute": lambda a: _run(f'cd /d "{a[0]}" && go test ./...')},
    "go_mod_init":        {"description": "Init Go module, args = [folder_path, module_name]",                "execute": lambda a: _run(f'cd /d "{a[0]}" && go mod init {a[1] if len(a)>1 else "main"}')},
    "go_mod_tidy":        {"description": "go mod tidy, args = [folder_path]",                               "execute": lambda a: _run(f'cd /d "{a[0]}" && go mod tidy')},
    "go_get":             {"description": "go get a package, args = [folder_path, package]",                  "execute": lambda a: _run(f'cd /d "{a[0]}" && go get {a[1]}')},
    "go_fmt":             {"description": "Format Go code, args = [folder_path]",                             "execute": lambda a: _run(f'cd /d "{a[0]}" && go fmt ./...')},
    "go_vet":             {"description": "Run go vet, args = [folder_path]",                                 "execute": lambda a: _run(f'cd /d "{a[0]}" && go vet ./...')},
    "go_version":         {"description": "Get Go version",                                                   "execute": lambda a: _run("go version")},

    "deno_run":           {"description": "Run a TypeScript/JS file with Deno, args = [file.ts]",             "execute": lambda a: _run(f'deno run --allow-all "{a[0]}"')},
    "deno_compile":       {"description": "Compile with Deno, args = [file.ts, output]",                      "execute": lambda a: _run(f'deno compile --allow-all -o "{a[1]}" "{a[0]}"')},
    "deno_test":          {"description": "Run Deno tests, args = [folder_path]",                             "execute": lambda a: _run(f'cd /d "{a[0]}" && deno test')},
    "deno_fmt":           {"description": "Format with Deno, args = [file_or_folder]",                        "execute": lambda a: _run(f'deno fmt "{a[0]}"')},
    "deno_lint":          {"description": "Lint with Deno, args = [file_or_folder]",                          "execute": lambda a: _run(f'deno lint "{a[0]}"')},
    "deno_version":       {"description": "Get Deno version",                                                  "execute": lambda a: _run("deno --version")},

    "ts_node_run":        {"description": "Run TypeScript with ts-node, args = [file.ts]",                    "execute": lambda a: _run(f'ts-node "{a[0]}"')},
    "tsc_compile":        {"description": "Compile TypeScript, args = [file.ts] or [folder]",                 "execute": lambda a: _run(f'tsc "{a[0]}"')},
    "tsc_watch":          {"description": "TypeScript watch mode, args = [folder_path]",                      "execute": lambda a: _run(f'cd /d "{a[0]}" && tsc --watch')},

    "dotnet_run":         {"description": "dotnet run, args = [folder_path]",                                 "execute": lambda a: _run(f'cd /d "{a[0]}" && dotnet run')},
    "dotnet_build":       {"description": "dotnet build, args = [folder_path]",                               "execute": lambda a: _run(f'cd /d "{a[0]}" && dotnet build')},
    "dotnet_test":        {"description": "dotnet test, args = [folder_path]",                                "execute": lambda a: _run(f'cd /d "{a[0]}" && dotnet test')},
    "dotnet_new":         {"description": "Create new dotnet project, args = [template, project_name]",       "execute": lambda a: _run(f'dotnet new {a[0]} -n {a[1] if len(a)>1 else "MyApp"}')},
    "dotnet_add_pkg":     {"description": "Add NuGet package, args = [folder_path, package]",                 "execute": lambda a: _run(f'cd /d "{a[0]}" && dotnet add package {a[1]}')},
    "dotnet_restore":     {"description": "dotnet restore, args = [folder_path]",                             "execute": lambda a: _run(f'cd /d "{a[0]}" && dotnet restore')},
    "dotnet_version":     {"description": "Get dotnet version",                                               "execute": lambda a: _run("dotnet --version")},

    "php_run":            {"description": "Run a PHP file, args = [file.php]",                                "execute": lambda a: _run(f'php "{a[0]}"')},
    "php_serve":          {"description": "Start PHP built-in server, args = [folder_path, port]",            "execute": lambda a: _run(f'cd /d "{a[0]}" && php -S localhost:{a[1] if len(a)>1 else "8080"}')},
    "php_composer_install":{"description": "composer install, args = [folder_path]",                          "execute": lambda a: _run(f'cd /d "{a[0]}" && composer install')},
    "php_version":        {"description": "Get PHP version",                                                  "execute": lambda a: _run("php --version")},

    "ruby_run":           {"description": "Run a Ruby file, args = [file.rb]",                                "execute": lambda a: _run(f'ruby "{a[0]}"')},
    "ruby_gem_install":   {"description": "Install a Ruby gem, args = [gem_name]",                            "execute": lambda a: _run(f"gem install {a[0]}")},
    "ruby_bundle":        {"description": "bundle install, args = [folder_path]",                             "execute": lambda a: _run(f'cd /d "{a[0]}" && bundle install')},
    "ruby_version":       {"description": "Get Ruby version",                                                 "execute": lambda a: _run("ruby --version")},

    "lua_run":            {"description": "Run a Lua file, args = [file.lua]",                                "execute": lambda a: _run(f'lua "{a[0]}"')},
    "lua_version":        {"description": "Get Lua version",                                                  "execute": lambda a: _run("lua -v")},

    "swift_run":          {"description": "Run a Swift file, args = [file.swift]",                            "execute": lambda a: _run(f'swift "{a[0]}"')},
    "swift_build":        {"description": "swift build, args = [folder_path]",                                "execute": lambda a: _run(f'cd /d "{a[0]}" && swift build')},
    "swift_test":         {"description": "swift test, args = [folder_path]",                                 "execute": lambda a: _run(f'cd /d "{a[0]}" && swift test')},
    "swift_version":      {"description": "Get Swift version",                                                 "execute": lambda a: _run("swift --version")},

    "kotlin_run":         {"description": "Compile and run a Kotlin file, args = [file.kt]",                  "execute": lambda a: _run(f'kotlinc "{a[0]}" -include-runtime -d out.jar && java -jar out.jar')},
    "kotlin_version":     {"description": "Get Kotlin version",                                               "execute": lambda a: _run("kotlinc -version")},

    "r_run":              {"description": "Run an R script, args = [file.R]",                                 "execute": lambda a: _run(f'Rscript "{a[0]}"')},
    "r_version":          {"description": "Get R version",                                                    "execute": lambda a: _run("Rscript --version")},

    "perl_run":           {"description": "Run a Perl script, args = [file.pl]",                              "execute": lambda a: _run(f'perl "{a[0]}"')},
    "perl_version":       {"description": "Get Perl version",                                                 "execute": lambda a: _run("perl --version")},
}

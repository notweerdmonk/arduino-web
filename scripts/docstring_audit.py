#!/usr/bin/env python3
"""AST-based docstring audit for medminder monorepo.

Usage: python3 scripts/docstring_audit.py
"""

import ast
import os
import sys
from collections import defaultdict

REPO = "/home/weerdmonk/Projects/medminder"

PACKAGES = {
    "arduino_dash": [
        "arduino_dash/python/arduino_dash/arduino_dash",
    ],
    "medminder_dash": [
        "medminder_dash/python/medminder_dash/medminder_dash",
    ],
    "board_manager": [
        "board_manager/python/board_manager/board_manager",
    ],
    "board_manager_client": [
        "board_manager_client/python/board_manager_client/board_manager_client",
    ],
    "grpc_client": [
        "grpc_client/python/arduino_grpc/arduino_grpc",
    ],
    "arduino_sketch_tools": [
        "arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools",
    ],
    "scripts": [
        "scripts",
    ],
}

EXCLUDE_FILES = {
    # __init__.py with NO code beyond imports — skip those
    "medminder_dash/python/medminder_dash/medminder_dash/__init__.py",
    # Tests
    "scripts/tests/conftest.py",
    "scripts/tests/test_setup_py.py",
    "scripts/tests/test_gen_grpc_bindings.py",
    # Self
    "scripts/docstring_audit.py",
}

EXCLUDE_DIRS = {
    "tests",
    "__pycache__",
    ".nox",
    ".ruff_cache",
    ".git",
    "_site",
    "node_modules",
    "build",
    "pyoxidizer",
    ".playwright-mcp",
}


def has_docstring(node):
    """Check if an AST node (module, class, function/async function) has a docstring."""
    body = node.body
    return bool(body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Str, ast.Constant)))


def analyze_file(filepath, pkg_name):
    """Analyze a single Python file for docstrings."""
    relpath = os.path.relpath(filepath, REPO).replace("\\", "/")
    
    if relpath in EXCLUDE_FILES:
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "filepath": filepath,
            "relpath": relpath,
            "package": pkg_name,
            "error": str(e),
            "module_docstring": False,
            "classes": [],
            "functions": [],
            "totals": {"classes": 0, "functions": 0, "missing": 0},
        }
    
    module_doc = has_docstring(tree)
    
    classes = []
    functions_found = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = has_docstring(node)
            classes.append({
                "name": node.name,
                "lineno": node.lineno,
                "docstring": doc,
            })
    
    # Find top-level functions and methods
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_doc = has_docstring(node)
            functions_found.append({
                "name": node.name,
                "lineno": node.lineno,
                "class": None,
                "docstring": func_doc,
            })
        elif isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_doc = has_docstring(child)
                    functions_found.append({
                        "name": child.name,
                        "lineno": child.lineno,
                        "class": node.name,
                        "docstring": method_doc,
                    })
    
    missing = 0
    if not module_doc:
        missing += 1
    for c in classes:
        if not c["docstring"]:
            missing += 1
    for f in functions_found:
        if not f["docstring"]:
            missing += 1
    
    return {
        "filepath": filepath,
        "relpath": relpath,
        "package": pkg_name,
        "module_docstring": module_doc,
        "classes": classes,
        "functions": functions_found,
        "totals": {
            "classes": len(classes),
            "functions": len(functions_found),
            "missing": missing,
        },
        "error": None,
    }


def collect_files():
    """Collect all .py files from the target packages."""
    files_by_pkg = defaultdict(list)
    
    for pkg_name, pkg_dirs in PACKAGES.items():
        for pkg_dir in pkg_dirs:
            pkg_path = os.path.join(REPO, pkg_dir)
            if not os.path.isdir(pkg_path):
                continue
            for root, dirs, filenames in os.walk(pkg_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    fpath = os.path.join(root, fn)
                    
                    # Skip _pb2.py and _pb2_grpc.py
                    if fn.endswith("_pb2.py") or fn.endswith("_pb2_grpc.py"):
                        continue
                    # Skip setup.py
                    if fn == "setup.py":
                        continue
                    
                    files_by_pkg[pkg_name].append(fpath)
    
    return files_by_pkg


def main():
    files_by_pkg = collect_files()
    
    all_results = []
    
    for pkg_name, filepaths in sorted(files_by_pkg.items()):
        print(f"\n{'='*80}")
        print(f"  PACKAGE: {pkg_name}")
        print(f"{'='*80}")
        
        pkg_functions = 0
        pkg_classes = 0
        pkg_missing = 0
        pkg_files = 0
        
        for fpath in sorted(filepaths):
            result = analyze_file(fpath, pkg_name)
            if result is None:
                continue
            
            all_results.append(result)
            pkg_files += 1
            pkg_functions += result["totals"]["functions"]
            pkg_classes += result["totals"]["classes"]
            pkg_missing += result["totals"]["missing"]
            
            relpath = result["relpath"]
            mod_doc = "YES" if result["module_docstring"] else "NO"
            print(f"\n  -- {relpath}")
            print(f"     Module docstring: {mod_doc}")
            
            if result["classes"]:
                print(f"     Classes ({len(result['classes'])}):")
                for c in result["classes"]:
                    status = "OK" if c["docstring"] else "MISSING"
                    print(f"       L{c['lineno']:>4} {c['name']:<30} [{status}]")
            
            if result["functions"]:
                print(f"     Functions/Methods ({len(result['functions'])}):")
                for f in result["functions"]:
                    status = "OK" if f["docstring"] else "MISSING"
                    ctx = f"(in {f['class']})" if f["class"] else ""
                    print(f"       L{f['lineno']:>4} {f['name']:<30} {ctx:<20} [{status}]")
        
        if pkg_files > 0:
            print(f"\n  -- Package Summary: {pkg_name} --")
            print(f"     Files: {pkg_files}")
            print(f"     Total classes:    {pkg_classes}")
            print(f"     Total functions:  {pkg_functions}")
            print(f"     Total missing docstrings: {pkg_missing}")
    
    # Grand totals
    print(f"\n{'='*80}")
    print(f"  GRAND TOTALS")
    print(f"{'='*80}")
    
    grand_files = 0
    grand_classes = 0
    grand_functions = 0
    grand_missing = 0
    
    for r in all_results:
        grand_files += 1
        grand_classes += r["totals"]["classes"]
        grand_functions += r["totals"]["functions"]
        grand_missing += r["totals"]["missing"]
    
    print(f"\n  Total files audited:  {grand_files}")
    print(f"  Total classes:        {grand_classes}")
    print(f"  Total functions:      {grand_functions}")
    print(f"  Total defs (class+func): {grand_classes + grand_functions}")
    print(f"  Total missing docstrings: {grand_missing}")
    if grand_classes + grand_functions > 0:
        pct = (grand_missing / (grand_classes + grand_functions)) * 100
        print(f"  Missing docstring rate: {pct:.1f}%")
    
    # Summary by package
    print(f"\n{'='*80}")
    print(f"  SUMMARY BY PACKAGE")
    print(f"{'='*80}")
    print(f"  {'Package':<25} {'Files':>6} {'Classes':>9} {'Funcs':>9} {'Missing':>9} {'Rate':>8}")
    print(f"  {'-'*25} {'-'*6} {'-'*9} {'-'*9} {'-'*9} {'-'*8}")
    
    by_pkg = defaultdict(lambda: {"files": 0, "classes": 0, "functions": 0, "missing": 0})
    for r in all_results:
        p = r["package"]
        by_pkg[p]["files"] += 1
        by_pkg[p]["classes"] += r["totals"]["classes"]
        by_pkg[p]["functions"] += r["totals"]["functions"]
        by_pkg[p]["missing"] += r["totals"]["missing"]
    
    for pkg_name in sorted(by_pkg.keys()):
        d = by_pkg[pkg_name]
        total_defs = d["classes"] + d["functions"]
        rate = (d["missing"] / total_defs * 100) if total_defs > 0 else 0
        print(f"  {pkg_name:<25} {d['files']:>6} {d['classes']:>9} {d['functions']:>9} {d['missing']:>9} {rate:>7.1f}%")
    
    print()
    
    # Detailed missing list
    print(f"\n{'='*80}")
    print(f"  DETAILED LIST OF ALL MISSING DOCSTRINGS")
    print(f"{'='*80}")
    
    total_missing_entries = 0
    for r in all_results:
        relpath = r["relpath"]
        had_missing = False
        
        if not r["module_docstring"]:
            print(f"\n  [{relpath}] Module-level docstring MISSING")
            total_missing_entries += 1
            had_missing = True
        
        for c in r["classes"]:
            if not c["docstring"]:
                if not had_missing:
                    print(f"\n  [{relpath}]")
                    had_missing = True
                print(f"    L{c['lineno']:>4}  CLASS  {c['name']}")
                total_missing_entries += 1
        
        for f in r["functions"]:
            if not f["docstring"]:
                if not had_missing:
                    print(f"\n  [{relpath}]")
                    had_missing = True
                ctx = f" (method of {f['class']})" if f["class"] else ""
                print(f"    L{f['lineno']:>4}  {'METHOD' if f['class'] else 'FUNC'}   {f['name']}{ctx}")
                total_missing_entries += 1
    
    print(f"\n  Total missing docstring entries: {total_missing_entries}")


if __name__ == "__main__":
    main()

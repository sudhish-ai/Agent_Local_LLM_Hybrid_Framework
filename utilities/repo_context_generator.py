# ALHF Repository Intelligence Generator
# Enhanced Version - Part 1
# Core Models + AST Intelligence Engine

import ast
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class CallCollector(ast.NodeVisitor):

    def __init__(self):
        self.calls = []

    def visit_Call(self, node):

        try:
            if isinstance(node.func, ast.Name):
                self.calls.append(node.func.id)

            elif isinstance(node.func, ast.Attribute):
                self.calls.append(node.func.attr)

        except Exception:
            pass

        self.generic_visit(node)


class RelationshipVisitor(ast.NodeVisitor):

    def __init__(self):

        self.classes = []
        self.functions = []
        self.imports = []

        self.methods = {}

        self.function_details = {}
        self.class_details = {}

        self.function_relationships = []
        self.class_relationships = []
        self.inheritance_graph = []

    def visit_Import(self, node):

        for name in node.names:
            self.imports.append(name.name)

        self.generic_visit(node)

    def visit_ImportFrom(self, node):

        if node.module:
            self.imports.append(node.module)

        self.generic_visit(node)

    def visit_ClassDef(self, node):

        class_name = node.name

        methods = []

        bases = []

        decorators = []

        for base in node.bases:

            if isinstance(base, ast.Name):
                bases.append(base.id)

                self.inheritance_graph.append(
                    {
                        "child": class_name,
                        "parent": base.id
                    }
                )

                self.class_relationships.append(
                    {
                        "source_class": class_name,
                        "relationship": "inherits",
                        "target_class": base.id
                    }
                )

        for decorator in node.decorator_list:

            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)

        self.classes.append(class_name)

        for child in node.body:

            if isinstance(
                child,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                methods.append(child.name)

        self.methods[class_name] = methods

        self.class_details[class_name] = {
            "name": class_name,
            "bases": bases,
            "decorators": decorators,
            "methods": methods
        }

        self.generic_visit(node)

    def visit_FunctionDef(self, node):

        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):

        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node):

        func_name = node.name

        parameters = []

        for arg in node.args.args:
            parameters.append(arg.arg)

        collector = CallCollector()
        collector.visit(node)

        return_type = None

        if node.returns:

            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id

        self.functions.append(func_name)

        self.function_details[func_name] = {
            "name": func_name,
            "parameters": parameters,
            "return_type": return_type,
            "calls": collector.calls
        }

        for target in collector.calls:

            self.function_relationships.append(
                {
                    "source_function": func_name,
                    "target_function": target
                }
            )


class RepositoryIntelligenceGenerator:

    IGNORE = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache"
    }

    EXTENSIONS = {
        ".py",
        ".json",
        ".yaml",
        ".yml",
        ".md",
        ".toml",
        ".ini",
        ".txt"
    }

    def __init__(self, repo_root: str):

        self.root = Path(repo_root)

        self.function_call_graph = []
        self.inheritance_graph = []

        self.module_catalog = {}
        self.file_catalog = {}

        self.dependency_graph = {}

        self.module_dependencies = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)

    def sha256(self, path: Path):

        h = hashlib.sha256()

        with open(path, "rb") as f:

            while True:

                block = f.read(8192)

                if not block:
                    break

                h.update(block)

        return h.hexdigest()

    def skip(self, path: Path):

        return any(
            part in self.IGNORE
            for part in path.parts
        )

    def build_tree(self, path: Path):

        tree = {}

        for child in sorted(path.iterdir()):

            if self.skip(child):
                continue

            if child.is_dir():
                tree[child.name] = self.build_tree(child)
            else:
                tree[child.name] = {}

        return tree

    def analyze_python(self, content: str):

        result = {
            "classes": [],
            "functions": [],
            "imports": [],
            "methods": {},
            "class_details": {},
            "function_details": {},
            "class_relationships": [],
            "function_relationships": [],
            "inheritance_graph": []
        }

        try:

            tree = ast.parse(content)

            visitor = RelationshipVisitor()

            visitor.visit(tree)

            result.update(
                {
                    "classes": visitor.classes,
                    "functions": visitor.functions,
                    "imports": visitor.imports,
                    "methods": visitor.methods,
                    "class_details": visitor.class_details,
                    "function_details": visitor.function_details,
                    "class_relationships": visitor.class_relationships,
                    "function_relationships": visitor.function_relationships,
                    "inheritance_graph": visitor.inheritance_graph
                }
            )

        except Exception as ex:

            result["parse_error"] = str(ex)

        return result

    def _get_module_name(self, relative_path: str):

        parent = str(Path(relative_path).parent)

        if parent == ".":
            return "root"

        return parent.replace("\\", "/")

    def _initialize_module(self, module_name: str):

        if module_name in self.module_catalog:
            return

        self.module_catalog[module_name] = {
            "module_name": module_name,

            "files": [],

            "classes": [],
            "functions": [],

            "imports": [],

            "class_details": {},
            "function_details": {},

            "call_graph": [],
            "inheritance_graph": [],

            "class_relationships": [],
            "function_relationships": [],

            "incoming_dependencies": [],
            "outgoing_dependencies": [],

            "impact_analysis": {},

            "statistics": {
                "file_count": 0,
                "class_count": 0,
                "function_count": 0
            }
        }

    def _update_module_catalog(
            self,
            module_name,
            file_path,
            py_result
    ):

        self._initialize_module(module_name)

        module = self.module_catalog[module_name]

        module["files"].append(file_path)

        module["classes"].extend(
            py_result["classes"]
        )

        module["functions"].extend(
            py_result["functions"]
        )

        module["imports"].extend(
            py_result["imports"]
        )

        module["class_relationships"].extend(
            py_result["class_relationships"]
        )

        module["function_relationships"].extend(
            py_result["function_relationships"]
        )

        module["inheritance_graph"].extend(
            py_result["inheritance_graph"]
        )

        module["class_details"].update(
            py_result["class_details"]
        )

        module["function_details"].update(
            py_result["function_details"]
        )

        for relation in py_result[
            "function_relationships"
        ]:
            module["call_graph"].append(
                {
                    "source": relation[
                        "source_function"
                    ],
                    "target": relation[
                        "target_function"
                    ]
                }
            )

        module["statistics"][
            "file_count"
        ] += 1

        module["statistics"][
            "class_count"
        ] += len(
            py_result["classes"]
        )

        module["statistics"][
            "function_count"
        ] += len(
            py_result["functions"]
        )

    def _build_reverse_dependencies(self):

        for source_module, dependencies in \
                self.module_dependencies.items():

            for dep in dependencies:
                self.reverse_dependencies[
                    dep
                ].add(
                    source_module
                )

    def _build_impact_analysis(self):

        impact_map = defaultdict(set)

        for module_name, module_data in \
                self.module_catalog.items():

            for relationship in module_data[
                "function_relationships"
            ]:
                source = relationship[
                    "source_function"
                ]

                target = relationship[
                    "target_function"
                ]

                impact_map[target].add(
                    source
                )

        for module_name, module_data in \
                self.module_catalog.items():
            module_data[
                "impact_analysis"
            ] = {
                func: sorted(
                    list(
                        impact_map.get(
                            func,
                            set()
                        )
                    )
                )
                for func in module_data[
                    "functions"
                ]
            }

    def _build_module_dependencies(self):

        for module_name, module_data in \
                self.module_catalog.items():

            deps = set()

            imports = module_data["imports"]

            for imp in imports:

                if not imp:
                    continue

                root_module = imp.split(".")[0]

                deps.add(root_module)

            self.module_dependencies[
                module_name
            ] = deps

        self._build_reverse_dependencies()

        for module_name in \
                self.module_catalog:
            self.module_catalog[
                module_name
            ][
                "outgoing_dependencies"
            ] = sorted(
                list(
                    self.module_dependencies.get(
                        module_name,
                        set()
                    )
                )
            )

            self.module_catalog[
                module_name
            ][
                "incoming_dependencies"
            ] = sorted(
                list(
                    self.reverse_dependencies.get(
                        module_name,
                        set()
                    )
                )
            )

    def scan_repository(self):

        repository_files = {}

        statistics = {
            "total_files": 0,
            "python_files": 0,
            "total_lines": 0,
            "total_classes": 0,
            "total_functions": 0
        }

        for file_path in self.root.rglob("*"):

            if not file_path.is_file():
                continue

            if self.skip(file_path):
                continue

            if (
                    file_path.suffix.lower()
                    not in self.EXTENSIONS
            ):
                continue

            relative_path = str(
                file_path.relative_to(
                    self.root
                )
            )

            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            file_entry = {
                "path": relative_path,
                "extension": file_path.suffix,
                "size_bytes":
                    file_path.stat().st_size,
                "line_count":
                    len(
                        text.splitlines()
                    ),
                "sha256":
                    self.sha256(
                        file_path
                    ),
                "content": text
            }

            statistics[
                "total_files"
            ] += 1

            statistics[
                "total_lines"
            ] += file_entry[
                "line_count"
            ]

            if (
                    file_path.suffix.lower()
                    == ".py"
            ):

                statistics[
                    "python_files"
                ] += 1

                python_info = (
                    self.analyze_python(
                        text
                    )
                )

                file_entry.update(
                    python_info
                )

                statistics[
                    "total_classes"
                ] += len(
                    python_info[
                        "classes"
                    ]
                )

                statistics[
                    "total_functions"
                ] += len(
                    python_info[
                        "functions"
                    ]
                )

                module_name = (
                    self._get_module_name(
                        relative_path
                    )
                )

                self._update_module_catalog(
                    module_name,
                    relative_path,
                    python_info
                )

                self.dependency_graph[
                    relative_path
                ] = python_info[
                    "imports"
                ]

                for rel in python_info[
                    "function_relationships"
                ]:
                    self.function_call_graph.append(
                        rel
                    )

                for rel in python_info[
                    "inheritance_graph"
                ]:
                    self.inheritance_graph.append(
                        rel
                    )

            repository_files[
                relative_path
            ] = file_entry

        self.file_catalog = (
            repository_files
        )

        self._build_module_dependencies()

        self._build_impact_analysis()

        return statistics

    def generate_repository_package(self):

        statistics = self.scan_repository()

        repository_package = {
            "project_name": self.root.name,

            "generated_at":
                datetime.utcnow().isoformat(),

            "generator_version":
                "2.0.0",

            "statistics":
                statistics,

            "directory_tree":
                self.build_tree(
                    self.root
                ),

            "module_catalog":
                self.module_catalog,

            "dependency_graph":
                self.dependency_graph,

            "repository_summary": {
                "total_modules":
                    len(
                        self.module_catalog
                    ),

                "total_files":
                    statistics[
                        "total_files"
                    ],

                "total_python_files":
                    statistics[
                        "python_files"
                    ],

                "total_classes":
                    statistics[
                        "total_classes"
                    ],

                "total_functions":
                    statistics[
                        "total_functions"
                    ]
            },

            "files":
                self.file_catalog
        }

        return repository_package

    def write_module_jsons(self):

        output_folder = Path(
            "module_knowledge"
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        manifest = {
            "generated_at":
                datetime.utcnow().isoformat(),
            "module_count":
                len(
                    self.module_catalog
                ),
            "modules": []
        }

        for module_name, module_data in \
                sorted(
                    self.module_catalog.items()
                ):

            safe_name = (
                module_name
                .replace("\\", "_")
                .replace("/", "_")
                .replace(":", "_")
            )

            if not safe_name:
                safe_name = "root"

            file_name = (
                f"{safe_name}.json"
            )

            output_file = (
                    output_folder / file_name
            )

            output_file.write_text(
                json.dumps(
                    module_data,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

            manifest[
                "modules"
            ].append(
                {
                    "module_name":
                        module_name,
                    "json_file":
                        file_name,
                    "class_count":
                        len(
                            module_data[
                                "classes"
                            ]
                        ),
                    "function_count":
                        len(
                            module_data[
                                "functions"
                            ]
                        )
                }
            )

        manifest_file = (
                output_folder /
                "manifest.json"
        )

        manifest_file.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    def write_repository_json(
            self,
            repository_package
    ):

        Path(
            "alhf_repository_knowledge_package.json"
        ).write_text(
            json.dumps(
                repository_package,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    # def write_consolidated_module_jsons(self):
    #
    #     output_folder = Path(
    #         "module_knowledge"
    #     )
    #
    #     output_folder.mkdir(
    #         parents=True,
    #         exist_ok=True
    #     )
    #
    #     module_groups = defaultdict(list)
    #
    #     #
    #     # Example:
    #     #
    #     # src/alhf_multi_agent_orchestrator/agents
    #     # src/alhf_multi_agent_orchestrator/contracts
    #     #
    #     # => src/alhf_multi_agent_orchestrator
    #     #
    #
    #     for module_name in self.module_catalog:
    #
    #         parts = module_name.split("/")
    #
    #         if len(parts) >= 2:
    #
    #             root_module = "/".join(
    #                 parts[:2]
    #             )
    #
    #         else:
    #
    #             root_module = module_name
    #
    #         module_groups[
    #             root_module
    #         ].append(
    #             module_name
    #         )
    #
    #     for root_module, child_modules in \
    #             module_groups.items():
    #
    #         consolidated = {
    #
    #             "module_name":
    #                 root_module,
    #
    #             "generated_at":
    #                 datetime.utcnow().isoformat(),
    #
    #             "children": {},
    #
    #             "statistics": {
    #                 "module_count": 0,
    #                 "file_count": 0,
    #                 "class_count": 0,
    #                 "function_count": 0
    #             },
    #
    #             "files": [],
    #             "classes": [],
    #             "functions": [],
    #             "imports": [],
    #
    #             "call_graph": [],
    #             "inheritance_graph": [],
    #
    #             "class_relationships": [],
    #             "function_relationships": [],
    #
    #             "incoming_dependencies": [],
    #             "outgoing_dependencies": [],
    #
    #             "impact_analysis": {}
    #         }
    #
    #         outgoing_deps = set()
    #         incoming_deps = set()
    #
    #         for child_module in child_modules:
    #
    #             child_data = self.module_catalog[
    #                 child_module
    #             ]
    #
    #             child_name = (
    #                 child_module
    #                 .replace(
    #                     root_module,
    #                     ""
    #                 )
    #                 .strip("/")
    #             )
    #
    #             if not child_name:
    #                 child_name = "root"
    #
    #             consolidated[
    #                 "children"
    #             ][
    #                 child_name
    #             ] = child_data
    #
    #             consolidated[
    #                 "files"
    #             ].extend(
    #                 child_data["files"]
    #             )
    #
    #             consolidated[
    #                 "classes"
    #             ].extend(
    #                 child_data["classes"]
    #             )
    #
    #             consolidated[
    #                 "functions"
    #             ].extend(
    #                 child_data["functions"]
    #             )
    #
    #             consolidated[
    #                 "imports"
    #             ].extend(
    #                 child_data["imports"]
    #             )
    #
    #             consolidated[
    #                 "call_graph"
    #             ].extend(
    #                 child_data["call_graph"]
    #             )
    #
    #             consolidated[
    #                 "inheritance_graph"
    #             ].extend(
    #                 child_data[
    #                     "inheritance_graph"
    #                 ]
    #             )
    #
    #             consolidated[
    #                 "class_relationships"
    #             ].extend(
    #                 child_data[
    #                     "class_relationships"
    #                 ]
    #             )
    #
    #             consolidated[
    #                 "function_relationships"
    #             ].extend(
    #                 child_data[
    #                     "function_relationships"
    #                 ]
    #             )
    #
    #             outgoing_deps.update(
    #                 child_data[
    #                     "outgoing_dependencies"
    #                 ]
    #             )
    #
    #             incoming_deps.update(
    #                 child_data[
    #                     "incoming_dependencies"
    #                 ]
    #             )
    #
    #             consolidated[
    #                 "impact_analysis"
    #             ].update(
    #                 child_data[
    #                     "impact_analysis"
    #                 ]
    #             )
    #
    #             consolidated[
    #                 "statistics"
    #             ][
    #                 "module_count"
    #             ] += 1
    #
    #             consolidated[
    #                 "statistics"
    #             ][
    #                 "file_count"
    #             ] += (
    #                 child_data[
    #                     "statistics"
    #                 ][
    #                     "file_count"
    #                 ]
    #             )
    #
    #             consolidated[
    #                 "statistics"
    #             ][
    #                 "class_count"
    #             ] += (
    #                 child_data[
    #                     "statistics"
    #                 ][
    #                     "class_count"
    #                 ]
    #             )
    #
    #             consolidated[
    #                 "statistics"
    #             ][
    #                 "function_count"
    #             ] += (
    #                 child_data[
    #                     "statistics"
    #                 ][
    #                     "function_count"
    #                 ]
    #             )
    #
    #         consolidated[
    #             "incoming_dependencies"
    #         ] = sorted(
    #             list(incoming_deps)
    #         )
    #
    #         consolidated[
    #             "outgoing_dependencies"
    #         ] = sorted(
    #             list(outgoing_deps)
    #         )
    #
    #         consolidated[
    #             "files"
    #         ] = sorted(
    #             list(
    #                 set(
    #                     consolidated["files"]
    #                 )
    #             )
    #         )
    #
    #         consolidated[
    #             "classes"
    #         ] = sorted(
    #             list(
    #                 set(
    #                     consolidated["classes"]
    #                 )
    #             )
    #         )
    #
    #         consolidated[
    #             "functions"
    #         ] = sorted(
    #             list(
    #                 set(
    #                     consolidated["functions"]
    #                 )
    #             )
    #         )
    #
    #         safe_name = (
    #             root_module
    #             .replace("/", "_")
    #             .replace("\\", "_")
    #         )
    #
    #         output_file = (
    #                 output_folder /
    #                 f"{safe_name}_consolidated.json"
    #         )
    #
    #         output_file.write_text(
    #             json.dumps(
    #                 consolidated,
    #                 indent=2,
    #                 ensure_ascii=False
    #             ),
    #             encoding="utf-8"
    #         )

    def write_consolidated_module_jsons(self):

        output_folder = Path(
            "module_knowledge"
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        module_groups = defaultdict(list)

        #
        # Group modules under feature boundary
        #

        for module_name in self.module_catalog.keys():
            consolidation_key = (
                self._get_consolidation_key(
                    module_name
                )
            )

            module_groups[
                consolidation_key
            ].append(
                module_name
            )

        for consolidated_module, child_modules in \
                sorted(
                    module_groups.items()
                ):

            consolidated = {

                "module_name":
                    consolidated_module,

                "generated_at":
                    datetime.utcnow().isoformat(),

                "statistics": {
                    "module_count": 0,
                    "file_count": 0,
                    "class_count": 0,
                    "function_count": 0
                },

                "children": {},

                "files": [],
                "classes": [],
                "functions": [],
                "imports": [],

                "call_graph": [],
                "inheritance_graph": [],

                "class_relationships": [],
                "function_relationships": [],

                "incoming_dependencies": [],
                "outgoing_dependencies": [],

                "impact_analysis": {}
            }

            incoming = set()
            outgoing = set()

            for child_module in child_modules:

                child_data = (
                    self.module_catalog[
                        child_module
                    ]
                )

                child_name = (
                    child_module
                    .replace(
                        consolidated_module,
                        ""
                    )
                    .strip("/")
                )

                if not child_name:
                    child_name = "root"

                consolidated[
                    "children"
                ][
                    child_name
                ] = child_data

                consolidated[
                    "files"
                ].extend(
                    child_data["files"]
                )

                consolidated[
                    "classes"
                ].extend(
                    child_data["classes"]
                )

                consolidated[
                    "functions"
                ].extend(
                    child_data["functions"]
                )

                consolidated[
                    "imports"
                ].extend(
                    child_data["imports"]
                )

                consolidated[
                    "call_graph"
                ].extend(
                    child_data["call_graph"]
                )

                consolidated[
                    "inheritance_graph"
                ].extend(
                    child_data[
                        "inheritance_graph"
                    ]
                )

                consolidated[
                    "class_relationships"
                ].extend(
                    child_data[
                        "class_relationships"
                    ]
                )

                consolidated[
                    "function_relationships"
                ].extend(
                    child_data[
                        "function_relationships"
                    ]
                )

                consolidated[
                    "impact_analysis"
                ].update(
                    child_data[
                        "impact_analysis"
                    ]
                )

                incoming.update(
                    child_data[
                        "incoming_dependencies"
                    ]
                )

                outgoing.update(
                    child_data[
                        "outgoing_dependencies"
                    ]
                )

                consolidated[
                    "statistics"
                ][
                    "module_count"
                ] += 1

                consolidated[
                    "statistics"
                ][
                    "file_count"
                ] += (
                    child_data[
                        "statistics"
                    ][
                        "file_count"
                    ]
                )

                consolidated[
                    "statistics"
                ][
                    "class_count"
                ] += (
                    child_data[
                        "statistics"
                    ][
                        "class_count"
                    ]
                )

                consolidated[
                    "statistics"
                ][
                    "function_count"
                ] += (
                    child_data[
                        "statistics"
                    ][
                        "function_count"
                    ]
                )

            consolidated[
                "incoming_dependencies"
            ] = sorted(
                incoming
            )

            consolidated[
                "outgoing_dependencies"
            ] = sorted(
                outgoing
            )

            consolidated[
                "files"
            ] = sorted(
                list(
                    set(
                        consolidated[
                            "files"
                        ]
                    )
                )
            )

            consolidated[
                "classes"
            ] = sorted(
                list(
                    set(
                        consolidated[
                            "classes"
                        ]
                    )
                )
            )

            consolidated[
                "functions"
            ] = sorted(
                list(
                    set(
                        consolidated[
                            "functions"
                        ]
                    )
                )
            )

            consolidated[
                "imports"
            ] = sorted(
                list(
                    set(
                        consolidated[
                            "imports"
                        ]
                    )
                )
            )

            file_name = (
                consolidated_module
                .replace(
                    "/",
                    "_"
                )
                .replace(
                    "\\",
                    "_"
                )
            )

            output_file = (
                    output_folder
                    /
                    f"{file_name}_consolidated.json"
            )

            output_file.write_text(
                json.dumps(
                    consolidated,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

    def _get_consolidation_key(
            self,
            module_name: str
    ):

        parts = module_name.split("/")

        #
        # Examples
        #
        # src/alhf/multi_agent_orchestrator/agents
        # -> src/alhf/multi_agent_orchestrator
        #
        # src/alhf/multi_agent_orchestrator/contracts
        # -> src/alhf/multi_agent_orchestrator
        #

        if len(parts) >= 3:
            return "/".join(parts[:3])

        if len(parts) == 2:
            return "/".join(parts[:2])

        return parts[0]

    # def run(self):
    #
    #     repository_package = (
    #         self.generate_repository_package()
    #     )
    #
    #     self.write_repository_json(
    #         repository_package
    #     )
    #
    #     self.write_module_jsons()
    #
    #     return repository_package

    def run(self):

        repository_package = (
            self.generate_repository_package()
        )

        self.write_repository_json(
            repository_package
        )

        self.write_module_jsons()

        self.write_consolidated_module_jsons()

        return repository_package

if __name__ == "__main__":
    REPO_ROOT = (
        r"D:\AI_Projects\Agent_Local_LLM_Hybrid_Framework"
    )

    generator = (
        RepositoryIntelligenceGenerator(
            REPO_ROOT
        )
    )

    repository_package = (
        generator.run()
    )

    print()

    print(
        "=" * 80)


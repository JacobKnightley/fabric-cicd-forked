# Changelog

The following contains all major, minor, and patch version release notes.

-   💥 Breaking change!
-   ✨ New Functionality
-   🔧 Bug Fix
-   📝 Documentation Update
-   ⚡ Internal Optimization

## Version 0.1.13

<span class="md-h2-subheader">Release Date: 2025-04-07</span>

-   ✨ Onboard Workspace Folders ([#81](https://github.com/microsoft/fabric-cicd/issues/81))
-   ✨ Onboard Variable Library item type ([#206](https://github.com/microsoft/fabric-cicd/issues/206))
-   ✨ Added support for Lakehouse Shortcuts
-   ✨ New `enable_environment_variable_replacement` feature flag ([#160](https://github.com/microsoft/fabric-cicd/issues/160))
-   ⚡ User-agent now available in API headers ([#207](https://github.com/microsoft/fabric-cicd/issues/207))
-   ⚡ Fixed error log typo in fabric_endpoint
-   🔧 Fix break with invalid optional parameters ([#192](https://github.com/microsoft/fabric-cicd/issues/192))
-   🔧 Fix bug where all workspace ids were not being replaced by parameterization ([#186](https://github.com/microsoft/fabric-cicd/issues/186))

## Version 0.1.12

<span class="md-h2-subheader">Release Date: 2025-03-27</span>

-   🔧 Fix constant overwrite failures ([#190](https://github.com/microsoft/fabric-cicd/issues/190))
-   🔧 Fix bug where all workspace ids were not being replaced ([#186](https://github.com/microsoft/fabric-cicd/issues/186))
-   🔧 Fix type hints for older versions of Python ([#156](https://github.com/microsoft/fabric-cicd/issues/156))
-   🔧 Fix accepted item types constant in pre-build

## Version 0.1.11

<span class="md-h2-subheader">Release Date: 2025-03-25</span>

-   💥 Parameterization refactor introducing a new parameter file structure and parameter file validation functionality ([#113](https://github.com/microsoft/fabric-cicd/issues/113))
-   📝 Update to [parameterization](https://microsoft.github.io/fabric-cicd/latest/how_to/parameterization/) docs
-   ✨ Support regex for publish exclusion ([#121](https://github.com/microsoft/fabric-cicd/issues/121))
-   ✨ Override max retries via constants ([#146](https://github.com/microsoft/fabric-cicd/issues/146))

## Version 0.1.10

<span class="md-h2-subheader">Release Date: 2025-03-19</span>

-   ✨ DataPipeline SPN Support ([#133](https://github.com/microsoft/fabric-cicd/issues/133))
-   🔧 Workspace ID replacement in data pipelines ([#164](https://github.com/microsoft/fabric-cicd/issues/164))
-   📝 Sample for passing in arguments from Azure DevOps Pipelines

## Version 0.1.9

<span class="md-h2-subheader">Release Date: 2025-03-11</span>

-   ✨ Support for Mirrored Database item type ([#145](https://github.com/microsoft/fabric-cicd/issues/145))
-   ⚡ Increase reserved name wait time ([#135](https://github.com/microsoft/fabric-cicd/issues/135))

## Version 0.1.8

<span class="md-h2-subheader">Release Date: 2025-03-04</span>

-   🔧 Handle null byPath object in report definition file ([#143](https://github.com/microsoft/fabric-cicd/issues/143))
-   🔧 Support relative directories ([#136](https://github.com/microsoft/fabric-cicd/issues/136)) ([#132](https://github.com/microsoft/fabric-cicd/issues/132))
-   🔧 Increase special character support ([#134](https://github.com/microsoft/fabric-cicd/issues/134))
-   ⚡ Changelog now available with version check ([#127](https://github.com/microsoft/fabric-cicd/issues/127))

## Version 0.1.7

<span class="md-h2-subheader">Release Date: 2025-02-26</span>

-   🔧 Fix special character support in files ([#129](https://github.com/microsoft/fabric-cicd/issues/129))

## Version 0.1.6

<span class="md-h2-subheader">Release Date: 2025-02-24</span>

-   ✨ Onboard Lakehouse item type ([#116](https://github.com/microsoft/fabric-cicd/issues/116))
-   📝 Update example docs ([#25](https://github.com/microsoft/fabric-cicd/issues/25))
-   📝 Update find_replace docs ([#110](https://github.com/microsoft/fabric-cicd/issues/110))
-   ⚡ Standardized docstrings to Google format
-   ⚡ Onboard file objects ([#46](https://github.com/microsoft/fabric-cicd/issues/46))
-   ⚡ Leverage UpdateDefinition Flag ([#28](https://github.com/microsoft/fabric-cicd/issues/28))
-   ⚡ Convert repo and workspace dictionaries ([#45](https://github.com/microsoft/fabric-cicd/issues/45))

## Version 0.1.5

<span class="md-h2-subheader">Release Date: 2025-02-18</span>

-   🔧 Fix Environment Failure without Public Library ([#103](https://github.com/microsoft/fabric-cicd/issues/103))
-   ⚡ Introduces pytest check for PRs ([#100](https://github.com/microsoft/fabric-cicd/issues/100))

## Version 0.1.4

<span class="md-h2-subheader">Release Date: 2025-02-12</span>

-   ✨ Support Feature Flagging ([#96](https://github.com/microsoft/fabric-cicd/issues/96))
-   🔧 Fix Image support in report deployment ([#88](https://github.com/microsoft/fabric-cicd/issues/88))
-   🔧 Fix Broken README link ([#92](https://github.com/microsoft/fabric-cicd/issues/92))
-   ⚡ Workspace ID replacement improved
-   ⚡ Increased error handling in activate script
-   ⚡ Onboard pytest and coverage
-   ⚡ Improvements to nested dictionaries ([#37](https://github.com/microsoft/fabric-cicd/issues/37))
-   ⚡ Support Python Installed From Windows Store ([#87](https://github.com/microsoft/fabric-cicd/issues/87))

## Version 0.1.3

<span class="md-h2-subheader">Release Date: 2025-01-29</span>

-   ✨ Add PyPI check version to encourage version bumps ([#75](https://github.com/microsoft/fabric-cicd/issues/75))
-   🔧 Fix Semantic model initial publish results in None Url error ([#61](https://github.com/microsoft/fabric-cicd/issues/61))
-   🔧 Fix Integer parsed as float failing in handle_retry for <3.12 python ([#63](https://github.com/microsoft/fabric-cicd/issues/63))
-   🔧 Fix Default item types fail to unpublish ([#76](https://github.com/microsoft/fabric-cicd/issues/76))
-   🔧 Fix Items in subfolders are skipped ([#77](https://github.com/microsoft/fabric-cicd/issues/77))
-   📝 Update documentation & examples

## Version 0.1.2

<span class="md-h2-subheader">Release Date: 2025-01-27</span>

-   ✨ Introduces max retry and backoff for long running / throttled calls ([#27](https://github.com/microsoft/fabric-cicd/issues/27))
-   🔧 Fix Environment publish uses arbitrary wait time ([#50](https://github.com/microsoft/fabric-cicd/issues/50))
-   🔧 Fix Environment publish doesn't wait for success ([#56](https://github.com/microsoft/fabric-cicd/issues/56))
-   🔧 Fix Long running operation steps out early for notebook publish ([#58](https://github.com/microsoft/fabric-cicd/issues/58))

## Version 0.1.1

<span class="md-h2-subheader">Release Date: 2025-01-23</span>

-   🔧 Fix Environment stuck in publish ([#51](https://github.com/microsoft/fabric-cicd/issues/51))

## Version 0.1.0

<span class="md-h2-subheader">Release Date: 2025-01-23</span>

-   ✨ Initial public preview release
-   ✨ Supports Notebook, Pipeline, Semantic Model, Report, and Environment deployments
-   ✨ Supports User and System Identity authentication
-   ✨ Released to PyPi
-   ✨ Onboarded to Github Pages

% ============================================================================
% METADATA KNOWLEDGE BASE - PROLOG RULES
% ============================================================================
% 
% This file contains business logic rules for querying metadata in a data catalog.
%
% DataPoint Structure (18 arguments):
%   datapoint(DatapointID, SubjectArea, ViewID, ViewName, ColumnName, ColumnLabel,
%             EnvironmentStatus, DbState, DataPointClass, Description,
%             SourceDatapointID, SourceViewIDName, SourceViewIDColumnName,
%             DataSteward, DataOwner, SensitivityLabel, SensitivityLabelRationale,
%             CriticalDataElementIndicator)
%
% Dataset Structure (12 arguments):
%   dataset(ViewID, ViewName, DataLayer, Name, SubjectArea, SubjectAreaSubCategory,
%           DataSource, DataSourceID, Reviewer, TechnicalDesignReviewer, Processor, Validator)

% ============================================================================
% HELPER PREDICATES
% ============================================================================

% Check if value is null/empty
is_null(null).
is_null('').

% Check if value is NOT null/empty
is_not_null(Value) :- \+ is_null(Value).

% ============================================================================
% DATASET QUERIES
% ============================================================================

% Find all datasets in a specific layer
datasets_in_layer(Layer, ViewName) :-
    dataset(_, ViewName, Layer, _, _, _, _, _, _, _, _, _).

% Find datasets by subject area
datasets_in_subject_area(SubjectArea, ViewName) :-
    dataset(_, ViewName, _, _, SubjectArea, _, _, _, _, _, _, _).

% Find datasets from a specific data source
datasets_from_source(DataSource, ViewName) :-
    dataset(_, ViewName, _, _, _, _, DataSource, _, _, _, _, _).

% Find datasets with specific layer AND subject area
datasets_filtered(Layer, SubjectArea, ViewName) :-
    dataset(_, ViewName, Layer, _, SubjectArea, _, _, _, _, _, _, _).

% Check if a dataset has a reviewer
has_reviewer(ViewName) :-
    dataset(_, ViewName, _, _, _, _, _, _, Reviewer, _, _, _),
    is_not_null(Reviewer).

% Check if a dataset has a validator
has_validator(ViewName) :-
    dataset(_, ViewName, _, _, _, _, _, _, _, _, _, Validator),
    is_not_null(Validator).

% ============================================================================
% GOVERNANCE RULES
% ============================================================================

% Find datasets missing reviewers
dataset_without_reviewer(ViewName) :-
    dataset(_, ViewName, _, _, _, _, _, _, Reviewer, _, _, _),
    is_null(Reviewer).

% Find datasets missing validators
dataset_without_validator(ViewName) :-
    dataset(_, ViewName, _, _, _, _, _, _, _, _, _, Validator),
    is_null(Validator).

% Find datasets missing both reviewer AND validator
dataset_with_governance_gap(ViewName) :-
    dataset(_, ViewName, _, _, _, _, _, _, Reviewer, _, _, Validator),
    is_null(Reviewer),
    is_null(Validator).

% Find Gold layer datasets without proper governance
gold_without_governance(ViewName) :-
    dataset(_, ViewName, 'Gold', _, _, _, _, _, Reviewer, _, _, Validator),
    (is_null(Reviewer) ; is_null(Validator)).

% ============================================================================
% DATA POINT QUERIES
% ============================================================================

% Find all datapoints in a specific view
datapoints_in_view(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, _, _, _, _, _, _, _, _, _, _, _).

% Find datapoints by subject area
datapoints_in_subject_area(SubjectArea, ViewName, ColumnName) :-
    datapoint(_, SubjectArea, _, ViewName, ColumnName, _, _, _, _, _, _, _, _, _, _, _, _, _).

% Find datapoints without data stewards
datapoint_without_steward(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, _, _, _, _, _, _, Steward, _, _, _, _),
    is_null(Steward).

% Find confidential/restricted data
confidential_data(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, _, _, _, _, _, _, _, _, SensitivityLabel, _, _),
    (SensitivityLabel = 'Confidential' ; SensitivityLabel = 'Restricted').

% Find PII data specifically
pii_data(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, _, _, _, _, _, _, _, _, _, Rationale, _),
    is_not_null(Rationale),
    (sub_string(Rationale, _, _, _, 'PII') ; sub_string(Rationale, _, _, _, 'personally identifiable')).

% Find critical data elements
critical_data(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, _, _, _, _, _, _, _, _, _, _, CriticalIndicator),
    CriticalIndicator = 'Yes'.

% ============================================================================
% LINEAGE QUERIES
% ============================================================================

% Find immediate source of a datapoint
% Arguments: datapoint(DP_ID, SubjectArea, ViewID, ViewName, ColumnName, ColumnLabel,
%                     EnvStatus, DbState, DPClass, Description,
%                     SourceDPID, SourceViewName, SourceColumnName,  <-- positions 11-13
%                     Steward, Owner, SensLabel, SensRationale, CriticalInd)
immediate_source(ViewName, ColumnName, SourceViewName, SourceColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, _, _, _, _, SourceViewName, SourceColumnName, _, _, _, _, _),
    is_not_null(SourceViewName),
    is_not_null(SourceColumnName).

% Full lineage trace with cycle detection
full_lineage(ViewName, ColumnName, Lineage) :-
    full_lineage_helper(ViewName, ColumnName, [ViewName-ColumnName], Lineage).

% Base case: no more sources
full_lineage_helper(ViewName, ColumnName, _Visited, []) :-
    \+ immediate_source(ViewName, ColumnName, _, _).

% Recursive case: follow the chain
full_lineage_helper(ViewName, ColumnName, Visited, [SourceView-SourceCol|Rest]) :-
    immediate_source(ViewName, ColumnName, SourceView, SourceCol),
    is_not_null(SourceView),
    is_not_null(SourceCol),
    \+ member(SourceView-SourceCol, Visited),  % Cycle detection
    full_lineage_helper(SourceView, SourceCol, [SourceView-SourceCol|Visited], Rest).

% Find all downstream dependencies (impact analysis)
downstream_impact(SourceView, SourceCol, TargetView, TargetCol) :-
    immediate_source(TargetView, TargetCol, SourceView, SourceCol).

% Find all downstream dependencies recursively
full_downstream_impact(SourceView, SourceCol, ImpactList) :-
    findall(Target-Column, 
            downstream_impact(SourceView, SourceCol, Target, Column),
            ImpactList).

% ============================================================================
% ENVIRONMENT QUERIES
% ============================================================================

% Find production datapoints
production_data(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, 'Production', _, _, _, _, _, _, _, _, _, _, _).

% Find deprecated datapoints
deprecated_data(ViewName, ColumnName) :-
    datapoint(_, _, _, ViewName, ColumnName, _, _, 'Deprecated', _, _, _, _, _, _, _, _, _, _).

% ============================================================================
% COMBINED GOVERNANCE RULES
% ============================================================================

% High risk: Confidential data without steward
high_risk_data(ViewName, ColumnName, 'No Data Steward') :-
    confidential_data(ViewName, ColumnName),
    datapoint_without_steward(ViewName, ColumnName).

% High risk: PII in production without steward
production_pii_without_steward(ViewName, ColumnName) :-
    production_data(ViewName, ColumnName),
    pii_data(ViewName, ColumnName),
    datapoint_without_steward(ViewName, ColumnName).

% Governance violation summary
governance_violation(ViewName, Violation) :-
    dataset_without_reviewer(ViewName),
    Violation = 'Missing Reviewer'.

governance_violation(ViewName, Violation) :-
    dataset_without_validator(ViewName),
    Violation = 'Missing Validator'.

% ============================================================================
% SUBJECT AREA ANALYSIS
% ============================================================================

% Check if subject area has complete pipeline (Bronze -> Silver -> Gold)
has_bronze(SubjectArea) :-
    dataset(_, _, 'Bronze', _, SubjectArea, _, _, _, _, _, _, _).

has_silver(SubjectArea) :-
    dataset(_, _, 'Silver', _, SubjectArea, _, _, _, _, _, _, _).

has_gold(SubjectArea) :-
    dataset(_, _, 'Gold', _, SubjectArea, _, _, _, _, _, _, _).

complete_pipeline(SubjectArea) :-
    has_bronze(SubjectArea),
    has_silver(SubjectArea),
    has_gold(SubjectArea).

incomplete_pipeline(SubjectArea) :-
    dataset(_, _, _, _, SubjectArea, _, _, _, _, _, _, _),
    \+ complete_pipeline(SubjectArea).

% ============================================================================
% DATA SOURCE ANALYSIS
% ============================================================================

% Check if data source reaches Gold layer
source_reaches_gold(DataSource) :-
    dataset(_, _, 'Gold', _, _, _, DataSource, _, _, _, _, _).

% Find all layers for a data source
source_layers(DataSource, Layer) :-
    dataset(_, _, Layer, _, _, _, DataSource, _, _, _, _, _).

% ============================================================================
% SUMMARY QUERIES
% ============================================================================

% Count datasets by layer
count_datasets_by_layer(Layer, Count) :-
    findall(ViewName, datasets_in_layer(Layer, ViewName), Views),
    length(Views, Count).

% Count datasets by subject area
count_datasets_by_subject_area(SubjectArea, Count) :-
    findall(ViewName, datasets_in_subject_area(SubjectArea, ViewName), Views),
    length(Views, Count).

% List all unique subject areas
all_subject_areas(SubjectAreas) :-
    findall(SA, dataset(_, _, _, _, SA, _, _, _, _, _, _, _), AllSAs),
    sort(AllSAs, SubjectAreas).

% List all unique data sources
all_data_sources(DataSources) :-
    findall(DS, dataset(_, _, _, _, _, _, DS, _, _, _, _, _), AllDSs),
    sort(AllDSs, DataSources).

% ============================================================================
% UTILITY PREDICATES
% ============================================================================

% Pretty print lineage
print_lineage([]).
print_lineage([View-Column|Rest]) :-
    format('  <- ~w.~w~n', [View, Column]),
    print_lineage(Rest).

% Print governance violations
print_governance_violations :-
    write('Governance Violations:\n'),
    forall(
        governance_violation(ViewName, Violation),
        format('  ~w: ~w~n', [ViewName, Violation])
    ).

% ============================================================================
% HELP / DOCUMENTATION
% ============================================================================

help :-
    write('=== Metadata Knowledge Base - Available Queries ===\n\n'),
    write('DATASET QUERIES:\n'),
    write('  datasets_in_layer(Layer, ViewName)\n'),
    write('  datasets_in_subject_area(SubjectArea, ViewName)\n'),
    write('  datasets_from_source(DataSource, ViewName)\n'),
    write('  datasets_filtered(Layer, SubjectArea, ViewName)\n\n'),
    write('GOVERNANCE:\n'),
    write('  dataset_without_reviewer(ViewName)\n'),
    write('  dataset_without_validator(ViewName)\n'),
    write('  gold_without_governance(ViewName)\n'),
    write('  datapoint_without_steward(ViewName, ColumnName)\n\n'),
    write('SENSITIVITY:\n'),
    write('  confidential_data(ViewName, ColumnName)\n'),
    write('  pii_data(ViewName, ColumnName)\n'),
    write('  critical_data(ViewName, ColumnName)\n\n'),
    write('LINEAGE:\n'),
    write('  immediate_source(ViewName, ColumnName, SourceView, SourceCol)\n'),
    write('  full_lineage(ViewName, ColumnName, Lineage)\n'),
    write('  downstream_impact(SourceView, SourceCol, TargetView, TargetCol)\n\n'),
    write('ANALYSIS:\n'),
    write('  complete_pipeline(SubjectArea)\n'),
    write('  source_reaches_gold(DataSource)\n'),
    write('  all_subject_areas(SubjectAreas)\n\n').
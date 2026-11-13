# HarborApiClient Python SDK 0.1.0<a id="harborapiclient-python-sdk-010"></a>

Welcome to the HarborApiClient SDK documentation. This guide will help you get started with integrating and using the HarborApiClient SDK in your project.

## Versions<a id="versions"></a>

- SDK version: `0.1.0`

## About the API<a id="about-the-api"></a>

To use this version of the API, send the `Harbor-API-Version: 2026-09-10.preview` header with every request. This is the latest version.

## Table of Contents<a id="table-of-contents"></a>

- [Setup & Configuration](#setup--configuration)
  - [Supported Language Versions](#supported-language-versions)
  - [Installation](#installation)
- [Authentication](#authentication)
  - [Access Token Authentication](#access-token-authentication)
- [Setting a Custom Timeout](#setting-a-custom-timeout)
- [Sample Usage](#sample-usage)
- [Services](#services)
- [Models](#models)
  - [Using Union Types](#using-union-types)

# Setup & Configuration<a id="setup--configuration"></a>

## Supported Language Versions<a id="supported-language-versions"></a>

This SDK is compatible with the following versions: `Python >= 3.9`

## Installation<a id="installation"></a>

To get started with the SDK, we recommend installing using `pip`:

```bash
pip install harbor-client
```

If you are using Python 3, you can use `pip3` instead:

```bash
pip3 install harbor-client
```

## Disabling Redirects<a id="disabling-redirects"></a>

By default, the SDK follows HTTP redirects (3xx responses) automatically. Pass
`follow_redirects=False` to get the redirect response back as-is instead:

```python
client = HarborAPIClient(follow_redirects=False)
```

This can also be changed later with `client.set_follow_redirects(False)`.

## Logging<a id="logging"></a>

The SDK is silent by default. Pass a standard library `logging.Logger` as `logger` to log
every outgoing request and its response (method, URL, status, and duration):

```python
import logging

logger = logging.getLogger("HarborAPIClient")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

client = HarborAPIClient(logger=logger)
```

This can also be changed later with `client.set_logging(logger)`.

`Authorization` and `Cookie` header values are always redacted in logged output, regardless
of the logger's own configuration.

## Authentication<a id="authentication"></a>

### Access Token Authentication<a id="access-token-authentication"></a>

The HarborAPIClient API uses an Access Token for authentication.

This token must be provided to authenticate your requests to the API.

#### Setting the Access Token<a id="setting-the-access-token"></a>

When you initialize the SDK, you can set the access token as follows:

```py
HarborAPIClient(
    token="YOUR_TOKEN",
    harbor_api_version="YOUR_HARBOR_API_VERSION",
    timeout=10
)
```

If you need to set or update the access token after initializing the SDK, you can use:

```py
sdk.set_access_token("YOUR_ACCESS_TOKEN")
```

## Setting a Custom Timeout<a id="setting-a-custom-timeout"></a>

You can set a custom timeout for the SDK's HTTP requests as follows:

```py
from harbor_client import HarborAPIClient

sdk = HarborAPIClient(timeout=10)
```

# Sample Usage<a id="sample-usage"></a>

Below is a comprehensive example demonstrating how to authenticate and call a simple endpoint:

```py
from harbor_client import HarborAPIClient
from harbor_client.types import RunState, JobsListRequestSort

client = HarborAPIClient(
    harbor_api_version="YOUR_HARBOR_API_VERSION",
)
response = client.jobs.list(
    task=[
        "task"
    ],
    state="queued",
    name="name",
    q="q",
    agent_name=[
        "agent_name"
    ],
    agent_version=[
        "agent_version"
    ],
    model_name=[
        "model_name"
    ],
    model_provider=[
        "model_provider"
    ],
    reasoning_effort=[
        "reasoning_effort"
    ],
    source=[
        "source"
    ],
    created_after="created_after",
    created_before="created_before",
    page_size="page_size",
    page_token="page_token",
    sort="id",
)
for item in response:
    print(item)
# alternatively, you can paginate page-by-page<a id="alternatively-you-can-paginate-page-by-page"></a>
for page in response.iter_pages():
    print(page)
```

# Async Usage<a id="async-usage"></a>

The SDK includes an Async Client for making asynchronous API requests. This is useful for applications that need non-blocking operations, like web servers or apps with a graphical user interface.

```py
import asyncio
from harbor_client import AsyncHarborAPIClient
from harbor_client.types import RunState, JobsListRequestSort

sdk = AsyncHarborAPIClient(
    harbor_api_version="YOUR_HARBOR_API_VERSION",
    timeout=10
)

task=[
    "task"
]
agent_name=[
    "agent_name"
]
agent_version=[
    "agent_version"
]
model_name=[
    "model_name"
]
model_provider=[
    "model_provider"
]
reasoning_effort=[
    "reasoning_effort"
]
source=[
    "source"
]

async def main():
  response_iterator = await sdk.jobs.list(
    task=task,
    state="queued",
    name="name",
    q="q",
    agent_name=agent_name,
    agent_version=agent_version,
    model_name=model_name,
    model_provider=model_provider,
    reasoning_effort=reasoning_effort,
    source=source,
    created_after="created_after",
    created_before="created_before",
    page_size="page_size",
    page_token="page_token",
    sort="id"
)
  for page in response_iterator:
    print(page)

asyncio.run(main())
```

## Services<a id="services"></a>

The SDK provides various services to interact with the API.

<details> 
<summary>Below is a list of all available services:</summary>

| Name          |
| :------------ |
| organizations |
| packages      |
| jobs          |
| trials        |
| rollouts      |
| account       |
| api_keys      |
| agents        |
| leaderboards  |
| secrets       |
| storage       |

</details>

## Models<a id="models"></a>

The SDK includes several models that represent the data structures used in API requests and responses. These models help in organizing and managing the data efficiently.

<details> 
<summary>Below is a list of all available models:</summary>

| Name                                           | Description |
| :--------------------------------------------- | :---------- |
| OrganizationDetail                             |             |
| OrganizationsEnsureRequest                     |             |
| EnsureOrganizationResponse                     |             |
| PackagesSetVisibilityRequest                   |             |
| SetPackageVisibilityResponse                   |             |
| PackagesUpdateOrganizationAccessRequest        |             |
| UpdatePackageAccessResponse                    |             |
| PackageAccess                                  |             |
| PackageVersionFilePage                         |             |
| PackageTag                                     |             |
| TagPackageVersionRequest                       |             |
| TagPackageVersionResponse                      |             |
| ReserveTemporaryPackageRequest                 |             |
| ReserveTemporaryTaskResponse                   |             |
| PackageVersionCatalogPage                      |             |
| PackagesListVersionCatalogRequestType          |             |
| PackagesListVersionCatalogRequestIncludeYanked |             |
| RegistryPackage                                |             |
| RegistryPackageVersionPage                     |             |
| PackagesListVersionsRequestIncludeYanked       |             |
| StorageDownload                                |             |
| JobSharing                                     |             |
| UpdateJobSharingRequest                        |             |
| JobTrialStatusItem                             |             |
| JobArtifactType                                |             |
| SubmitJobRequest                               |             |
| JobResponse                                    |             |
| JobsRenameRequest                              |             |
| RenameJobResponse                              |             |
| DeleteJobsRequest                              |             |
| DeleteJobsResponse                             |             |
| JobsTransferRequest                            |             |
| TransferJobResponse                            |             |
| JobsCopyRequest                                |             |
| StorageCopyResult                              |             |
| JobActionRequest                               |             |
| JobActionResponse                              |             |
| CancelJobsRequest                              |             |
| JobPage                                        |             |
| RunState                                       |             |
| JobsListRequestSort                            |             |
| FilterValuesResponse                           |             |
| JobsGetFiltersRequestField                     |             |
| JobTaskPage                                    |             |
| JobsListTasksRequestSortBy                     |             |
| JobsListTasksRequestSortOrder                  |             |
| ResultJobCreate                                |             |
| CreatedResultJob                               |             |
| JobOverview                                    |             |
| JobsGetOverviewRequestForceCombined            |             |
| EvaluationComparison                           |             |
| TrialResponse                                  |             |
| TrialArtifactType                              |             |
| TrialActionRequest                             |             |
| TrialActionResponse                            |             |
| CancelTrialsRequest                            |             |
| RetryTrialsRequest                             |             |
| RetryTrialsResponse                            |             |
| TrialsCopyRequest                              |             |
| TrialsGetFiltersRequestField                   |             |
| TrialPage                                      |             |
| TrialsListRequestSort                          |             |
| ResultTrialCreate                              |             |
| CreatedResultTrial                             |             |
| RolloutResponse                                |             |
| RolloutActionRequest                           |             |
| CancelRolloutsRequest                          |             |
| RetryRolloutsRequest                           |             |
| RetryRolloutsResponse                          |             |
| RolloutsGetFiltersRequestField                 |             |
| TrialPage1                                     |             |
| RolloutsListRequestSort                        |             |
| AccountIdentity                                |             |
| MyOrganizationsItem                            |             |
| ApiKeyMetadataPage                             |             |
| ApiKeyCreate                                   |             |
| ApiKeyCreated                                  |             |
| AgentsResponse                                 |             |
| LeaderboardDetail                              |             |
| LeaderboardsUpdateRequest                      |             |
| UpdateLeaderboardResponse                      |             |
| LeaderboardRowDetail                           |             |
| LeaderboardRowsPage                            |             |
| LeaderboardSummaryPage                         |             |
| LeaderboardsCreateRequest                      |             |
| CreateLeaderboardResponse                      |             |
| LeaderboardTrialLinkPage                       |             |
| SecretMetadataPage                             |             |
| SecretsListRequestStatusFilter                 |             |
| SecretsUpsertRequest                           |             |
| SecretWriteResult                              |             |
| SecretsRevokeRequest                           |             |
| SecretsRevokeResponse                          |             |
| SecretsPreflightRequest                        |             |
| SecretPreflight                                |             |
| SecretsListRegistryCredentialsResponse         |             |
| SecretsListRegistryCredentialsRequestStatus    |             |
| RegistryCredentialUpsertEncoded                |             |
| RegistryCredential                             |             |
| RegistryCredentialRevokeResult                 |             |
| SecretsRevokeRegistryCredentialRequestPurge    |             |
| StorageUploadSession                           |             |
| StorageUploadReceipt                           |             |
| PackageNameReference                           |             |
| PackageAccessOrganizationSummary               |             |
| PackageOrganizationGrant                       |             |
| PackagePublicGrant                             |             |
| PackageAccessGrantCreator                      |             |
| TaskVersionDetail                              |             |
| DatasetVersionDetail                           |             |
| TaskEnvironmentRequirement                     |             |
| ResolvedTaskStep                               |             |
| DatasetVersionFile                             |             |
| DatasetVersionRevisionSummary                  |             |
| TaskVersionManifest                            |             |
| DatasetVersionManifest                         |             |
| RegistryVersionFile                            |             |
| UnavailableDatasetTaskDependency               |             |
| AvailableDatasetTaskDependency                 |             |
| PackageVersionSummary                          |             |
| RegistryPackageVersion                         |             |
| JobOwnerOrganization                           |             |
| JobShareOrganizationSummary                    |             |
| JobCreator                                     |             |
| HostedDiffSelectors                            |             |
| HostedAgentConfig                              |             |
| HostedSubmissionEnvironmentConfig              |             |
| HostedSubmissionTaskConfig                     |             |
| HostedSubmissionDatasetConfig                  |             |
| HostedSubmissionRetryConfig                    |             |
| HostedVerifierConfig                           |             |
| MetricConfig                                   |             |
| HostedGithubAgentSource                        |             |
| HostedSecretSelection                          |             |
| HostedSubmissionCredentialProxyPolicyRule      |             |
| HostedSubmissionCredentialProxyRequestMatch    |             |
| CredentialProxyHeaderTransform                 |             |
| HostedSubmissionCredentialProxyPathMatch       |             |
| ArtifactConfig                                 |             |
| HostedJobTrialRegradeSource                    |             |
| SubmitJobResponse                              |             |
| DryRunResponse                                 |             |
| OwnerOrganization                              |             |
| SelectedSecret                                 |             |
| AgentSource                                    |             |
| AgentSourceManifest                            |             |
| AgentSourceRuntime                             |             |
| JobDetail                                      |             |
| TrialCounts                                    |             |
| MeanAggregate                                  |             |
| UsageAggregates                                |             |
| SumAggregate                                   |             |
| JobSummary                                     |             |
| JobTaskSummary                                 |             |
| JobRewardMetricSet                             |             |
| EvaluationJobReference                         |             |
| EvaluationSummary                              |             |
| JobManualPauseSummary                          |             |
| JobCancellationSummary                         |             |
| JobOverviewStatistics                          |             |
| JobCircuitState                                |             |
| JobBucketCircuitState                          |             |
| EvaluationSummaryRow                           |             |
| JobPackageRunTarget                            |             |
| JobPathRunTarget                               |             |
| EvaluationMetricSet                            |             |
| EvaluationComparisonTask                       |             |
| EvaluationComparisonAgentModel                 |             |
| EvaluationComparisonCell                       |             |
| TrialDetail                                    |             |
| TaskIdentity                                   |             |
| AgentIdentity                                  |             |
| ModelIdentity                                  |             |
| Usage                                          |             |
| TrialSummary                                   |             |
| ResultModelUsage                               |             |
| TrialDetail1                                   |             |
| ApiKeyMetadata                                 |             |
| LeaderboardDefinition                          |             |
| LeaderboardReadColumnDefinition                |             |
| LeaderboardReadRankingRule                     |             |
| CreateLeaderboardRowInput                      |             |
| LeaderboardWriteColumnDefinition               |             |
| LeaderboardWriteRankingRule                    |             |
| LeaderboardMutationRecord                      |             |
| LeaderboardMutationRow                         |             |
| LeaderboardChangeSummary                       |             |
| LeaderboardRankedRow                           |             |
| LeaderboardSummary                             |             |
| LeaderboardTrialLink                           |             |
| SecretMetadata                                 |             |
| HostedLocalTaskRequirements                    |             |
| HostedPreflightEnvironmentConfig               |             |
| HostedTaskConfig                               |             |
| HostedDatasetConfig                            |             |
| HostedRetryConfig                              |             |
| CredentialProxyPolicyRule                      |             |
| CredentialProxyRequestMatch                    |             |
| CredentialProxyPathMatch                       |             |
| HostedTaskEnvironmentRequirement               |             |
| RegistryCredentialSummary                      |             |
| StorageTaskUploadCreate                        |             |
| StorageDatasetUploadCreate                     |             |
| StorageJobUploadCreate                         |             |
| StorageTrialUploadCreate                       |             |
| StorageUploadFileInput                         |             |
| StorageTaskUploadMetadata                      |             |
| TaskPublishStep                                |             |
| StoragePublicationFile                         |             |
| StorageDatasetUploadMetadata                   |             |
| DatasetPublishTaskReference                    |             |
| StorageJobUploadMetadata                       |             |
| StorageUploadFile                              |             |
| StorageTaskUploadResult                        |             |
| StorageDatasetUploadResult                     |             |
| StorageResultUploadResult                      |             |
| StorageHttpTransfer                            |             |
| StorageTusTransfer                             |             |
| BadRequestEncoded                              |             |
| InvalidPageSizeEncoded                         |             |
| InvalidPageTokenEncoded                        |             |
| RegistryCredentialReplacementRequiredEncoded   |             |
| RegistryCredentialReplacementStaleEncoded      |             |
| ExistingRegistryCredential                     |             |
| UnauthorizedEncoded                            |             |
| NotFoundEncoded                                |             |
| InternalServerErrorEncoded                     |             |
| ForbiddenEncoded                               |             |
| ConflictEncoded                                |             |
| TooManyRequestsEncoded                         |             |
| ServiceUnavailableEncoded                      |             |
| SecretReplacementRequiredEncoded               |             |
| SecretReplacementStaleEncoded                  |             |
| ExistingSecretSummary                          |             |

</details>

### Using Union Types<a id="using-union-types"></a>

Union types allow you to specify that a variable can have more than one type. This is particularly useful when a function can accept multiple types of inputs. The Union type hint is used for this purpose.

#### Example Function with Union Types<a id="example-function-with-union-types"></a>

You can call service method with an instance of `TypeA`, `TypeB`, or a dictionary that can be converted to an instance of either type.

```python
# Model Definition<a id="model-definition"></a>
ParamType = Union[TypeA, TypeB]

# Service Method<a id="service-method"></a>
def service_method(param: ParamType):
...

## Usage<a id="usage"></a>
type_a = TypeA(key="value")
type_b = TypeB(key="value")

sdk.service.service_method(type_a)
sdk.service.service_method(type_b)
sdk.service.service_method({"key": "value"})
```

You cannot create an instance of a `Union` type itself. Instead, pass an instance of one of the types in the `Union`, or a dictionary that can be converted to one of those types.

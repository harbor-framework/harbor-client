from harbor_client import HarborAPIClient

client = HarborAPIClient(
    harbor_api_version="YOUR_HARBOR_API_VERSION",
)
response = client.jobs.list(
    task=["task"],
    state="queued",
    name="name",
    q="q",
    agent_name=["agent_name"],
    agent_version=["agent_version"],
    model_name=["model_name"],
    model_provider=["model_provider"],
    reasoning_effort=["reasoning_effort"],
    source=["source"],
    created_after="created_after",
    created_before="created_before",
    page_size="page_size",
    page_token="page_token",
    sort="id",
)
for item in response:
    print(item)
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    print(page)

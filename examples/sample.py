from harbor_client import HarborAPIClient
from harbor_client.types import (
    JobsListRequestScope,
    JobsListRequestAccess,
    JobsListRequestArchive,
    JobsListRequestSort,
)

client = HarborAPIClient(
    harbor_api_version="YOUR_HARBOR_API_VERSION",
)
response = client.jobs.list(
    page_size="page_size",
    page_token="page_token",
    offset="offset",
    search="search",
    agents="agents",
    providers="providers",
    models="models",
    date_="date",
    scope="my",
    shared_with_organization_id="eB1fbaFE-8057-91Ab-e599-fF4BE1FefE95",
    datasets="datasets",
    access="owned",
    owner_organization_id="A961822f-aE15-4fBd-61fc-bdFA1a0c4bf1",
    date_from="date_from",
    date_to="date_to",
    created_by="aF923390-7cd1-4f3d-B212-e447f11BCCa2",
    archive="current",
    sort="importance",
)
for item in response:
    print(item)
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    print(page)
